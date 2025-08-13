import http from "./http";
import { clearTokens, setTokens, Tokens } from "../utils/tokens";

export type LoginInput = {
  username: string;
  password: string;
};

export type RegisterInput = {
  username: string;
  email: string;
  password: string;
  password2: string;
};

export type User = {
  id: number;
  username: string;
  email: string;
  tokens: number;
  money: number;
  is_staff: boolean;
  has_club: boolean;
};

export type LoginResponse = {
  access: string;
  refresh: string;
  user: User;
};

export async function login(data: LoginInput): Promise<LoginResponse> {
  try {
    const res = await http.post<LoginResponse>("/api/auth/login/", data);
    const { access, refresh, user } = res.data;
    setTokens({ access, refresh });
    return { access, refresh, user };
  } catch (err: any) {
    const detail =
      err?.response?.data?.detail ||
      err?.response?.data?.non_field_errors?.[0] ||
      "Ошибка входа. Проверьте логин и пароль.";
    throw new Error(detail);
  }
}

export async function register(data: RegisterInput): Promise<User> {
  try {
    const res = await http.post<User>("/api/auth/register/", data);
    return res.data;
  } catch (err: any) {
    // Соберём поля ошибок в удобочитаемую строку
    const data = err?.response?.data;
    if (data && typeof data === "object") {
      const messages: string[] = [];
      for (const [field, value] of Object.entries(data as Record<string, any>)) {
        if (Array.isArray(value)) {
          messages.push(`${field}: ${value.join(", ")}`);
        } else {
          messages.push(`${field}: ${String(value)}`);
        }
      }
      throw new Error(messages.join(" | "));
    }
    throw new Error("Ошибка регистрации.");
  }
}

export async function getCurrentUser(): Promise<User> {
  try {
    const res = await http.get<User>("/api/auth/user/");
    return res.data;
  } catch (err: any) {
    const detail =
      err?.response?.data?.detail ||
      "Не удалось получить данные пользователя.";
    throw new Error(detail);
  }
}

export async function refreshTokens(): Promise<Tokens> {
  try {
    // Обычно это делает интерцептор, но предоставим явную функцию на всякий случай
    const res = await http.post<Tokens>("/api/auth/refresh/", {});
    const { access, refresh } = res.data as any;
    setTokens({ access, refresh });
    return { access, refresh };
  } catch (err: any) {
    throw new Error("Не удалось обновить токен.");
  }
}

export async function logout(refresh?: string): Promise<void> {
  try {
    if (refresh) {
      await http.post("/api/auth/logout/", { refresh });
    }
  } catch {
    // Игнорируем ошибку логаута на сервере, всё равно чистим локальные токены
  } finally {
    clearTokens();
  }
}
