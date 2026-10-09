package com.ruoyi.framework.web.service;

import com.ruoyi.common.core.domain.entity.SysFamily;
import com.ruoyi.common.core.domain.model.LoginUser;
import com.ruoyi.common.enums.UserStatus;
import com.ruoyi.common.exception.ServiceException;
import com.ruoyi.system.service.ISysFamilyService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;
import java.util.HashSet;
import java.util.Set;

/**
 * 家属用户验证处理
 *
 * @author ruoyi
 */
@Service("familyUserDetailsService")
public class FamilyUserDetailsService implements UserDetailsService
{
    private static final Logger log = LoggerFactory.getLogger(FamilyUserDetailsService.class);

    @Autowired
    private ISysFamilyService sysFamilyService;
    
    @Autowired
    private SysPermissionService permissionService;

    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException
    {
        SysFamily family = sysFamilyService.selectSysFamilyByPhoneNumber(username);
        if (family == null)
        {
            log.info("登录家属：{} 不存在.", username);
            throw new UsernameNotFoundException("登录家属：" + username + " 不存在");
        }
        else if (UserStatus.DELETED.getCode().equals(family.getDelFlag()))
        {
            log.info("登录家属：{} 已被删除.", username);
            throw new ServiceException("对不起，您的账号：" + username + " 已被删除");
        }
        else if (UserStatus.DISABLE.getCode().equals(family.getStatus()))
        {
            log.info("登录家属：{} 已被停用.", username);
            throw new ServiceException("对不起，您的账号：" + username + " 已停用");
        }

        return createLoginUser(family);
    }

    public UserDetails createLoginUser(SysFamily family)
    {
        Set<String> permissions = new HashSet<>();
        permissions.add("*:*:*"); // 暂给所有权限，或根据需求限制
        return new LoginUser(family, permissions);
    }
}
