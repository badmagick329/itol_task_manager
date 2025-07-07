// This is the expected shape of JSON responses from the API.
// This is not enforced and the backend is just expected to not violate this shape.
export type ApiResponse = {
  ok: boolean;
  status?: number;
  redirect?: string;
  message?: string;
  data?: object;
  error?: string;
};
