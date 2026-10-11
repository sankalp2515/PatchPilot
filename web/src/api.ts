export async function api<T>(path: string, options?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch("/api" + path, options);
  } catch {
    throw new Error(
      "Cannot reach the PatchPilot backend. Start the local server and retry connection.",
    );
  }
  if (!response.ok) {
    let message = "Request failed. Try again.";
    try {
      const data = await response.json();
      message =
        typeof data.detail === "string"
          ? data.detail
          : "Check the incident fields and JSON acceptance cases.";
    } catch {
      /* fall back to bounded message */
    }
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}
export const post = <T>(path: string, body?: unknown) =>
  api<T>(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });
export function downloadText(text: string, name: string) {
  const url = URL.createObjectURL(
    new Blob([text], { type: "text/plain;charset=utf-8" }),
  );
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
