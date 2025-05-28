package com.yxg.history.mapper;
import com.yxg.history.pojo.History;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

import java.time.LocalDateTime;
import java.util.List;

@Mapper
public interface HistoryMapper {

    @Select("select * from hist where id = #{id} order by time desc limit #{page},5")
    List<History> selectByPage(int id, int page);

    @Select("select * from hist where time = #{time} and type = #{type}")
    History selectByTime(String time, String type);
}
