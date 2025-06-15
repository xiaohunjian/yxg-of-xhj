package com.yxg.history.service;

import com.sun.xml.internal.ws.policy.privateutil.PolicyUtils;
import com.yxg.history.pojo.Result;

import java.io.IOException;
import java.nio.file.Path;

public interface PreService {
    Result prediction(String time, String name, Path uploadPath, String type,String filename) throws IOException;

}
