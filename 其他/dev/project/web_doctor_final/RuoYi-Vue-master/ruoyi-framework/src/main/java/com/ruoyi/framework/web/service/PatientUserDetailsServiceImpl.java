package com.ruoyi.framework.web.service;

import com.ruoyi.common.core.domain.entity.PatientUser;
import com.ruoyi.common.core.domain.model.LoginUser;
import com.ruoyi.common.enums.UserStatus;
import com.ruoyi.common.exception.ServiceException;
import com.ruoyi.common.utils.StringUtils;
import com.ruoyi.system.service.IPatientUserService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

/**
 * 病人用户验证处理 (专门为 patient_user 表服务)
 *
 * @author ruoyi (modified by you)
 */
@Service("patientUserDetailsService") // 给这个Bean一个唯一的名字，避免和原始的冲突
public class PatientUserDetailsServiceImpl implements UserDetailsService {
    private static final Logger log = LoggerFactory.getLogger(PatientUserDetailsServiceImpl.class);

    @Autowired
    private IPatientUserService patientUserService;

    // 注意：这里我们暂时不注入权限服务，因为病人可能没有复杂的角色权限
    // @Autowired
    // private SysPermissionService permissionService;

    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        // 1. 根据手机号从 patient_user 表查询用户
        PatientUser patientUser = patientUserService.selectPatientUserByPhonenumber(username);

        // 2. 对查询结果进行校验
        if (StringUtils.isNull(patientUser)) {
            log.info("登录用户：{} 不存在.", username);
            throw new UsernameNotFoundException("登录用户：" + username + " 不存在");
        } else if (UserStatus.DELETED.getCode().equals(patientUser.getDelFlag())) {
            log.info("登录用户：{} 已被删除.", username);
            throw new ServiceException("对不起，您的账号：" + username + " 已被删除");
        } else if (UserStatus.DISABLE.getCode().equals(patientUser.getStatus())) {
            log.info("登录用户：{} 已被停用.", username);
            throw new ServiceException("对不起，您的账号：" + username + " 已停用");
        }

        // 3. 校验通过后，创建 Spring Security 需要的 UserDetails 对象
        return createLoginUser(patientUser);
    }

    public UserDetails createLoginUser(PatientUser patientUser) {
        // 将 PatientUser 对象 转换为 LoginUser 对象
        // 调用我们为 PatientUser 新增的构造函数
        return new LoginUser(patientUser, new java.util.HashSet<>());
    }
}
