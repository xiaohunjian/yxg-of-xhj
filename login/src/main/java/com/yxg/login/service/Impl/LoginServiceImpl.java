package com.yxg.login.service.Impl;

import com.yxg.login.mapper.LoginMapper;
import com.yxg.login.pojo.LoginReq;
import com.yxg.login.pojo.PasswordUtil;
import com.yxg.login.pojo.Result;
import com.yxg.login.pojo.User;
import com.yxg.login.service.LoginService;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import javax.crypto.SecretKey;
import java.io.File;
import java.util.Base64;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

@Service
public class LoginServiceImpl implements LoginService {
    @Value("${jwt.key}")
    private String secretKey;

    @Autowired
    private LoginMapper loginMapper;

    @Override
    public Result login(LoginReq loginReq) {
        User user1 =loginMapper.findByName(loginReq.getName());
        if(user1==null){
            return new Result(400,"name or password wrong","");
        }
        if(PasswordUtil.checkPassword(loginReq.getPassword(),user1.getPassword())){
            return new Result(200,"success",genjwt(user1));
        }
        else{
            return new Result(400,"name or password wrong","");
        }
    }

    @Override
    public Result register(User user) {
        String name = user.getName();
        if(loginMapper.findByName(name)!=null){
            return new Result(400,"user has exist","");
        }
        user.setPassword(PasswordUtil.hashPassword(user.getPassword()));
        loginMapper.register(user.getName(), user.getPassword());
        File folder = new File("C:\\Users\\yijian\\Desktop\\project\\yxg\\user\\"+user.getName());
        folder.mkdirs();
        return new Result(200,"success","");
    }


    String genjwt(User user) {
        Map<String,Object> map = new HashMap<>();
        byte[] decodedKey = Base64.getDecoder().decode(secretKey);
        SecretKey key = Keys.hmacShaKeyFor(decodedKey);;
        map.put("id",user.getId());
        map.put("name",user.getName());
        map.put("password",user.getPassword());
        String jwt = Jwts.builder()
                .signWith(SignatureAlgorithm.HS256,key)
                .claims(map)
                .expiration(new Date(System.currentTimeMillis() + 1000*60*60*24))
                .compact();
        return jwt;
    }
}
