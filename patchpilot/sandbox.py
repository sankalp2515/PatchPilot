"""A bounded data transformation interpreter. Never exec/eval user or model code."""

import ast
import copy
import json
import math
import operator

BUILTINS = {
    "isinstance": isinstance,
    "len": len,
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "sum": sum,
    "min": min,
    "max": max,
    "sorted": sorted,
    "list": list,
    "dict": dict,
    "abs": abs,
    "round": round,
    "enumerate": enumerate,
}
METHODS = {
    dict: {"get", "keys", "values", "items"},
    list: {"append", "extend", "count"},
    str: {"lower", "upper", "strip", "startswith", "endswith", "split", "replace"},
}
ALLOWED = (
    ast.Module,
    ast.FunctionDef,
    ast.arguments,
    ast.arg,
    ast.Return,
    ast.Assign,
    ast.AugAssign,
    ast.Expr,
    ast.If,
    ast.For,
    ast.Pass,
    ast.Break,
    ast.Continue,
    ast.Name,
    ast.Load,
    ast.Store,
    ast.Constant,
    ast.Dict,
    ast.List,
    ast.Tuple,
    ast.Subscript,
    ast.Slice,
    ast.Attribute,
    ast.Call,
    ast.keyword,
    ast.BinOp,
    ast.UnaryOp,
    ast.BoolOp,
    ast.Compare,
    ast.IfExp,
    ast.ListComp,
    ast.GeneratorExp,
    ast.comprehension,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.FloorDiv,
    ast.Mod,
    ast.USub,
    ast.UAdd,
    ast.Not,
    ast.And,
    ast.Or,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.LtE,
    ast.Gt,
    ast.GtE,
    ast.In,
    ast.NotIn,
    ast.Is,
    ast.IsNot,
)
BINARY = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
}
COMPARE = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
    ast.In: lambda a, b: a in b,
    ast.NotIn: lambda a, b: a not in b,
    ast.Is: operator.is_,
    ast.IsNot: operator.is_not,
}


def validate_code(code, entrypoint):
    if len(code) > 12000:
        raise ValueError("Code size limit exceeded")
    try:
        tree = ast.parse(code)
    except (SyntaxError, RecursionError) as exc:
        raise ValueError("Adapter must be valid Python") from exc
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.FunctionDef):
        raise ValueError(
            "Supply exactly one adapter function; imports and top-level operations are prohibited"
        )
    fn = tree.body[0]
    if (
        fn.name != entrypoint
        or len(fn.args.args) != 1
        or fn.args.vararg
        or fn.args.kwarg
        or fn.decorator_list
    ):
        raise ValueError("Adapter must match the entrypoint and accept exactly one JSON input")
    if fn.args.posonlyargs or fn.args.kwonlyargs or fn.args.defaults:
        raise ValueError("Adapter arguments cannot have defaults or extra parameters")
    for node in ast.walk(tree):
        if not isinstance(node, ALLOWED):
            raise ValueError(f"Unsupported operation: {type(node).__name__}")
        if isinstance(node, ast.FunctionDef) and node is not fn:
            raise ValueError("Nested functions are prohibited")
        if isinstance(node, ast.Name) and "__" in node.id:
            raise ValueError("Dunder identifiers are prohibited")
        if isinstance(node, ast.Attribute) and (
            node.attr.startswith("_") or node.attr not in set().union(*METHODS.values())
        ):
            raise ValueError("Only safe JSON methods are allowed")
        if isinstance(node, ast.Call) and not (
            isinstance(node.func, ast.Name)
            and node.func.id in BUILTINS
            or isinstance(node.func, ast.Attribute)
            and node.func.attr in set().union(*METHODS.values())
        ):
            raise ValueError("Only allowlisted JSON operations can be called")
        if isinstance(node, ast.comprehension) and node.is_async:
            raise ValueError("Async comprehensions are prohibited")
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and abs(node.value) > 1e12:
            raise ValueError("Numeric literal limit exceeded")
    return fn


class Returned(Exception):
    def __init__(self, value):
        self.value = value


class Flow(Exception):
    pass


class Interpreter:
    def __init__(self):
        self.steps = 0

    def tick(self):
        self.steps += 1
        if self.steps > 20000:
            raise ValueError("Operation limit exceeded")

    def bounded(self, value):
        if isinstance(value, (str, list, tuple, dict)) and len(value) > 100000:
            raise ValueError("Output size limit exceeded")
        if isinstance(value, (int, float)) and (not math.isfinite(value) or abs(value) > 1e15):
            raise ValueError("Numeric limit exceeded")
        return value

    def json_budget(self, value):
        stack = [(value, 0)]
        count = 0
        while stack:
            self.tick()
            item, depth = stack.pop()
            count += 1
            if count > 20000 or depth > 30:
                raise ValueError("Nested data size limit exceeded")
            if isinstance(item, dict):
                if count + len(stack) + len(item) > 20000:
                    raise ValueError("Nested data queue limit exceeded")
                stack.extend((child, depth + 1) for child in item.values())
            elif isinstance(item, (list, tuple)):
                if count + len(stack) + len(item) > 20000:
                    raise ValueError("Nested data queue limit exceeded")
                stack.extend((child, depth + 1) for child in item)
        return value

    def assign(self, target, value, env):
        self.tick()
        if isinstance(target, ast.Name):
            env[target.id] = value
        elif isinstance(target, (ast.Tuple, ast.List)):
            if len(target.elts) != len(value):
                raise ValueError("Unpacking mismatch")
            for item, val in zip(target.elts, value):
                self.assign(item, val, env)
        elif isinstance(target, ast.Subscript):
            self.expr(target.value, env)[self.expr(target.slice, env)] = value
        else:
            raise ValueError("Unsupported assignment")

    def block(self, nodes, env):
        for node in nodes:
            self.tick()
            if isinstance(node, ast.Return):
                raise Returned(self.expr(node.value, env) if node.value else None)
            elif isinstance(node, ast.Assign):
                value = self.expr(node.value, env)
                for target in node.targets:
                    self.assign(target, value, env)
            elif isinstance(node, ast.AugAssign):
                value = self.binary(node.op, self.expr(node.target, env), self.expr(node.value, env))
                self.assign(node.target, value, env)
            elif isinstance(node, ast.Expr):
                self.expr(node.value, env)
            elif isinstance(node, ast.If):
                self.block(node.body if self.expr(node.test, env) else node.orelse, env)
            elif isinstance(node, ast.For):
                broken = False
                for item in self.expr(node.iter, env):
                    self.tick()
                    self.assign(node.target, item, env)
                    try:
                        self.block(node.body, env)
                    except Flow as exc:
                        if str(exc) == "break":
                            broken = True
                            break
                if not broken:
                    self.block(node.orelse, env)
            elif isinstance(node, (ast.Break, ast.Continue)):
                raise Flow("break" if isinstance(node, ast.Break) else "continue")
            elif not isinstance(node, ast.Pass):
                raise ValueError("Unsupported statement")

    def binary(self, op, a, b):
        if isinstance(op, ast.Mult):
            seq, n = (a, b) if isinstance(a, (str, list, tuple)) else (b, a)
            if isinstance(seq, (str, list, tuple)) and isinstance(n, int) and len(seq) * max(n, 0) > 100000:
                raise ValueError("Output size limit exceeded")
            if isinstance(a, (int, float)) and isinstance(b, (int, float)) and abs(a) * abs(b) > 1e15:
                raise ValueError("Numeric limit exceeded")
        if isinstance(op, ast.Mod) and isinstance(a, str):
            raise ValueError("String formatting is prohibited")
        return self.bounded(BINARY[type(op)](a, b))

    def expr(self, node, env):
        self.tick()
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            if node.id in env:
                return env[node.id]
            if node.id in {"dict", "list", "str"}:
                return BUILTINS[node.id]
            raise ValueError(f"Unknown variable: {node.id}")
        if isinstance(node, ast.Dict):
            if any(k is None for k in node.keys):
                raise ValueError("Dictionary unpacking is prohibited")
            return {self.expr(k, env): self.expr(v, env) for k, v in zip(node.keys, node.values)}
        if isinstance(node, (ast.List, ast.Tuple)):
            return [self.expr(x, env) for x in node.elts]
        if isinstance(node, ast.Subscript):
            return self.expr(node.value, env)[self.expr(node.slice, env)]
        if isinstance(node, ast.Slice):
            return slice(*(self.expr(x, env) if x else None for x in (node.lower, node.upper, node.step)))
        if isinstance(node, ast.BinOp):
            return self.binary(node.op, self.expr(node.left, env), self.expr(node.right, env))
        if isinstance(node, ast.UnaryOp):
            return {ast.Not: operator.not_, ast.USub: operator.neg, ast.UAdd: operator.pos}[type(node.op)](
                self.expr(node.operand, env)
            )
        if isinstance(node, ast.BoolOp):
            value = None
            for item in node.values:
                value = self.expr(item, env)
                if isinstance(node.op, ast.And) and not value or isinstance(node.op, ast.Or) and value:
                    break
            return value
        if isinstance(node, ast.Compare):
            a = self.expr(node.left, env)
            for op, other in zip(node.ops, node.comparators):
                b = self.expr(other, env)
                if not COMPARE[type(op)](a, b):
                    return False
                a = b
            return True
        if isinstance(node, ast.IfExp):
            return self.expr(node.body if self.expr(node.test, env) else node.orelse, env)
        if isinstance(node, (ast.ListComp, ast.GeneratorExp)):
            result = []

            def collect(index, scope):
                self.tick()
                if index == len(node.generators):
                    result.append(self.expr(node.elt, scope))
                    return
                gen = node.generators[index]
                for item in self.expr(gen.iter, scope):
                    next_scope = dict(scope)
                    self.assign(gen.target, item, next_scope)
                    if all(self.expr(cond, next_scope) for cond in gen.ifs):
                        collect(index + 1, next_scope)

            collect(0, dict(env))
            return self.bounded(result)
        if isinstance(node, ast.Call):
            args = [self.expr(a, env) for a in node.args]
            kwargs = {k.arg: self.expr(k.value, env) for k in node.keywords}
            if None in kwargs:
                raise ValueError("Keyword unpacking is prohibited")
            if isinstance(node.func, ast.Name):
                if kwargs:
                    raise ValueError("Builtin keyword arguments are prohibited")
                for argument in args:
                    self.json_budget(argument)
                value = BUILTINS[node.func.id](*args)
                if node.func.id == "enumerate":
                    value = list(value)
            else:
                obj = self.expr(node.func.value, env)
                if node.func.attr not in METHODS.get(type(obj), set()):
                    raise ValueError("Method unavailable on this JSON value")
                if node.func.attr == "extend" and args and len(obj) + len(args[0]) > 100000:
                    raise ValueError("List growth limit exceeded")
                if node.func.attr == "append" and len(obj) >= 100000:
                    raise ValueError("List growth limit exceeded")
                if (
                    node.func.attr == "replace"
                    and len(args) >= 2
                    and len(str(obj)) * max(1, len(str(args[1]))) > 100000
                ):
                    raise ValueError("Output size limit exceeded")
                value = getattr(obj, node.func.attr)(*args, **kwargs)
                if node.func.attr in {"keys", "values", "items"}:
                    value = list(value)
            return self.bounded(value)
        raise ValueError(f"Unsupported expression: {type(node).__name__}")


def verify(code, entrypoint, cases):
    try:
        fn = validate_code(code, entrypoint)
    except ValueError as exc:
        return [
            {"name": c["name"], "passed": False, "expected": c["expected"], "actual": None, "error": str(exc)}
            for c in cases
        ]
    results = []
    for case in cases:
        try:
            interpreter = Interpreter()
            scope = {fn.args.args[0].arg: copy.deepcopy(case["input"])}
            try:
                interpreter.block(fn.body, scope)
                actual = None
            except Returned as value:
                actual = value.value
            interpreter.json_budget(actual)
            serialized = json.dumps(actual, allow_nan=False, sort_keys=True)
            if len(serialized) > 100000:
                raise ValueError("Output size limit exceeded")
            actual = json.loads(serialized)
            results.append(
                {
                    "name": case["name"],
                    "passed": serialized == json.dumps(case["expected"], allow_nan=False, sort_keys=True),
                    "expected": case["expected"],
                    "actual": actual,
                    "error": "",
                }
            )
        except Exception as exc:
            results.append(
                {
                    "name": case["name"],
                    "passed": False,
                    "expected": case["expected"],
                    "actual": None,
                    "error": f"{type(exc).__name__}: {str(exc)[:300]}",
                }
            )
    return results
