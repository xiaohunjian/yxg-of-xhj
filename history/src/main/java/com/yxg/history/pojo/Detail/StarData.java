package com.yxg.history.pojo.Detail;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class StarData {
    public List<DetailStar> first;
    public List<DetailStar> second;
    public List<DetailStar> third;
}
