import axios, { AxiosError, AxiosInstance, AxiosRequestConfig } from "axios";
import { clearTokens, getAccessToken, getRefreshToken, setTokens } from "../utils/tokens";

// Базовая конфигурация API
const apiBaseURL = "http://localhost:8000";

// Создаем инстанс axios
const http: AxiosInstance = axios.create({
  baseURL: apiBaseURL,
  withCredentials: false, // JWT в заголовках, куки не используем
  headers: {
    "Content-Type": "application/json",
  },
});

// Флаг и очередь для предотвращения множественных одновременных refresh
let isRefreshing = false;
let refreshQueue: Array<{
  resolve: (value?: unknown) => void;
  reject: (reason?: any) => void;
}> = [];

function subscribeTokenRefresh(resolve: (value?: unknown) => void, reject: (reason?: any) => void) {
  refreshQueue.push({ resolve, reject });
}

function onRefreshed() {
  refreshQueue.forEach((p) => p.resolve());
  refreshQueue = [];
}

function onRefreshedError(err: any) {
  refreshQueue.forEach((p) => p.reject(err));
  refreshQueue = [];
}

// Добавляем access токен в каждый запрос
http.interceptors.request.use((config) => {
  const access = getAccessToken();
  if (access) {
    config.headers = config.headers ?? {};
    (config.headers as Record<string, string>)["Authorization"] = `Bearer ${access}`;
  }
  return config;
});

// Обработка 401 — пробуем обновить access токен через refresh
http.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };
    const status = error.response?.status;

    // Если не авторизация — просто пробрасываем дальше
    if (status !== 401) {
      return Promise.reject(error);
    }

    // Если уже пробовали — не зацикливаемся
    if (originalRequest._retry) {
      return Promise.reject(error);
    }
    originalRequest._retry = true;

    const refresh = getRefreshToken();
    if (!refresh) {
      // Нет refresh — чистим токены и выходим
      clearTokens();
      return Promise.reject(error);
    }

    // Если refresh уже в процессе — подписываемся на завершение
    if (isRefreshing) {
      try {
        await new Promise((resolve, reject) => subscribeTokenRefresh(resolve, reject));
        // После успешного refresh пробуем повторить запрос
        return http(originalRequest);
      } catch (e) {
        return Promise.reject(e);
      }
    }

    // Выполняем refresh
    isRefreshing = true;
    try {
      const resp = await axios.post(
        `${apiBaseURL}/api/auth/refresh/`,
        { refresh },
        { headers: { "Content-Type": "application/json" } }
      );
      const newAccess = (resp.data as any).access as string;
      const newRefresh = (resp.data as any).refresh as string | undefined;

      setTokens({ access: newAccess, refresh: newRefresh ?? refresh });
      onRefreshed();

      // Повторяем исходный запрос с новым access
      return http(originalRequest);
    } catch (refreshErr) {
      onRefreshedError(refreshErr);
      clearTokens();
      return Promise.reject(refreshErr);
    } finally {
      isRefreshing = false;
    }
  }
);

export default http;
