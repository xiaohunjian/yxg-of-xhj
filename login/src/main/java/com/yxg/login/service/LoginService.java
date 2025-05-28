package com.yxg.login.service;

import com.yxg.login.pojo.LoginReq;
import com.yxg.login.pojo.Result;
import com.yxg.login.pojo.User;

public interface LoginService {
    Result login(LoginReq loginReq);

    Result register(User user);
}
