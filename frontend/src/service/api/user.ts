import AppAxios, { type ResponseWrapper } from "../request";

export const login = (payload: any) => {
  return AppAxios.post<ResponseWrapper<string>>("/user/login", payload);
};

export const register = (payload: any) => {
  return AppAxios.post<ResponseWrapper<string>>("/user/register", payload);
};

export const logout = () => {
  return AppAxios.post<ResponseWrapper<boolean>>("/user/logout");
};

export const changePassword = (payload: any) => {
  return AppAxios.post<ResponseWrapper<string>>(
    "/user/change_password",
    payload
  );
};

export const getQSARToken = () => {
  return AppAxios.get<ResponseWrapper<string>>("/user/token_check");
};
export const getQSARTokenByApp = (payload: {
  appAccessKey: string;
  clientName: string;
}) => {
  return AppAxios.post<ResponseWrapper<string>>(
    "/user/get_token_by_cookie",
    payload
  );
};
