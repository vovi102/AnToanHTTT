const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type ApiDetail = { message?: string; permission?: string };

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public permission?: string,
  ) {
    super(message);
  }
}

export async function apiRequest<T>(
  path: string,
  token?: string | null,
  options: RequestInit = {},
): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
      },
    });
  } catch {
    throw new ApiError(0, "Không thể kết nối máy chủ FastAPI");
  }

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const detail: string | ApiDetail = body.detail ?? "Yêu cầu thất bại";
    throw new ApiError(
      response.status,
      typeof detail === "string" ? detail : detail.message ?? "Yêu cầu thất bại",
      typeof detail === "object" ? detail.permission : undefined,
    );
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export { API_BASE };
