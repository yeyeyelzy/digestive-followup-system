package com.ruoyi.framework.web.service;

import com.ruoyi.common.core.domain.model.LoginUser;
import com.ruoyi.common.exception.ServiceException;
import com.ruoyi.common.exception.user.UserPasswordNotMatchException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

/**
 * 患者端登录服务。
 */
@Component
public class PatientLoginService {

    @Autowired
    private TokenService tokenService;

    @Autowired
    @Qualifier("patientUserDetailsService")
    private UserDetailsService patientUserDetailsService;

    @Autowired
    private PasswordEncoder passwordEncoder;

    public String login(String phoneNumber, String password) {
        UserDetails userDetails;
        try {
            userDetails = patientUserDetailsService.loadUserByUsername(phoneNumber);
        } catch (Exception e) {
            throw new ServiceException("登录患者：" + phoneNumber + " 不存在");
        }

        if (!passwordEncoder.matches(password, userDetails.getPassword())) {
            throw new UserPasswordNotMatchException();
        }

        LoginUser loginUser = (LoginUser) userDetails;
        return tokenService.createToken(loginUser);
    }
}
