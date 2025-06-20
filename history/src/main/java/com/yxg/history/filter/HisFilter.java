package com.yxg.history.filter;

import com.yxg.history.pojo.Result;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import javax.servlet.*;
import javax.servlet.annotation.WebFilter;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import com.alibaba.fastjson.JSONObject;
import org.springframework.beans.factory.annotation.Value;

import javax.crypto.SecretKey;
import java.io.IOException;
import java.util.Base64;

@WebFilter
public class HisFilter implements Filter {
    @Value("${jwt.key}")
    private String secretKey;

    @Override
    public void doFilter(ServletRequest servletRequest, ServletResponse servletResponse, FilterChain filterChain) throws IOException, ServletException {
        HttpServletRequest req = (HttpServletRequest) servletRequest;
        HttpServletResponse resp = (HttpServletResponse) servletResponse;
        String url = req.getRequestURI().toString();
        String jwt = req.getHeader("Token");
        if(jwt==null){
            System.out.println("未检测到令牌");
            Result res = new Result(400,"please login","");
            String json = JSONObject.toJSONString(res);
            resp.getWriter().write(json);
            return;
        }
        try{
            byte[] decodedKey = Base64.getDecoder().decode(secretKey);
            SecretKey key = Keys.hmacShaKeyFor(decodedKey);
            Claims claims = Jwts.parser()
                    .verifyWith(key)
                    .build()
                    .parseSignedClaims(jwt)
                    .getPayload();
            req.setAttribute("id",claims.get("id",Integer.class));
            req.setAttribute("name",claims.get("name",String.class));
        }catch (Exception e){
            e.printStackTrace();
            System.out.println("令牌解析失败");
            Result res = new Result(400,"fall","");
            String notLogin = JSONObject.toJSONString(res);
            resp.getWriter().write(notLogin);
            return;
        }
        filterChain.doFilter(servletRequest, servletResponse);
    }

}
