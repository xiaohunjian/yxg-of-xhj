package com.yxg.history.mapper;

import com.yxg.history.pojo.History;
import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

@Mapper
public interface PreMapper {

    @Select("select id from user where name = #{name}")
    int findByName(String name);

    @Insert("insert into hist(id, time, addr, type,fileName ) VALUES (#{id},#{time},#{addr},#{type},#{fileName})")
    void addFile(History history);

    @Select("select addr from hist where id = #{id} and time = #{time}")
    String getFile(int id, String time);
}
