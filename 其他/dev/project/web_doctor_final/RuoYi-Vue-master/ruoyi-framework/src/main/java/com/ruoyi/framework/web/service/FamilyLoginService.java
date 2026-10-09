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
 * 家属登录服务
 */
@Component
public class FamilyLoginService {

    @Autowired
    private TokenService tokenService;

    @Autowired
    @Qualifier("familyUserDetailsService")
    private UserDetailsService familyUserDetailsService;

    @Autowired
    private PasswordEncoder passwordEncoder;

    public String login(String phoneNumber, String password) {
        UserDetails userDetails;
        try {
            userDetails = familyUserDetailsService.loadUserByUsername(phoneNumber);
        } catch (Exception e) {
            throw new ServiceException("登录家属：" + phoneNumber + " 不存在");
        }

        if (!passwordEncoder.matches(password, userDetails.getPassword())) {
            throw new UserPasswordNotMatchException();
        }

        LoginUser loginUser = (LoginUser) userDetails;
        return tokenService.createToken(loginUser);
    }
}
