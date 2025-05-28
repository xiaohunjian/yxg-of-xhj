package com.yxg.login.mapper;

import com.yxg.login.pojo.User;
import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

@Mapper
public interface LoginMapper {
    @Select("select * from user where id = #{id}")
    User findById(int id);

    @Select("select * from user where name = #{name}")
    User findByName(String name);

    @Insert("INSERT INTO user(name,password) VALUES(#{name}, #{password})")
    void register(String name, String password);
}
