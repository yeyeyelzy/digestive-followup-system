package com.ruoyi.system.domain;

import org.apache.commons.lang3.builder.ToStringBuilder;
import org.apache.commons.lang3.builder.ToStringStyle;
import com.ruoyi.common.annotation.Excel;
import com.ruoyi.common.core.domain.BaseEntity;

/**
 * 医生管理对象 doctor
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
public class Doctor extends BaseEntity
{
    private static final long serialVersionUID = 1L;

    /** 医生id */
    private Long doctorId;

    /** 医生姓名 */
    @Excel(name = "医生姓名")
    private String doctorName;

    /** 电话 */
    @Excel(name = "电话")
    private String phoneNumber;

    /** 密码 */
    @Excel(name = "密码")
    private String password;

    /** 头像 */
    @Excel(name = "头像")
    private String avatarUrl;

    /** 角色权限（1-->医生 2--> 护士 读写权限） */
    @Excel(name = "角色权限", readConverterExp = "1=-->医生,2=-->,护=士,读=写权限")
    private Long role;

    public void setDoctorId(Long doctorId) 
    {
        this.doctorId = doctorId;
    }

    public Long getDoctorId() 
    {
        return doctorId;
    }
    public void setDoctorName(String doctorName) 
    {
        this.doctorName = doctorName;
    }

    public String getDoctorName() 
    {
        return doctorName;
    }
    public void setPhoneNumber(String phoneNumber) 
    {
        this.phoneNumber = phoneNumber;
    }

    public String getPhoneNumber() 
    {
        return phoneNumber;
    }
    public void setPassword(String password) 
    {
        this.password = password;
    }

    public String getPassword() 
    {
        return password;
    }
    public void setAvatarUrl(String avatarUrl) 
    {
        this.avatarUrl = avatarUrl;
    }

    public String getAvatarUrl() 
    {
        return avatarUrl;
    }
    public void setRole(Long role) 
    {
        this.role = role;
    }

    public Long getRole() 
    {
        return role;
    }

    @Override
    public String toString() {
        return new ToStringBuilder(this,ToStringStyle.MULTI_LINE_STYLE)
            .append("doctorId", getDoctorId())
            .append("doctorName", getDoctorName())
            .append("phoneNumber", getPhoneNumber())
            .append("password", getPassword())
            .append("avatarUrl", getAvatarUrl())
            .append("role", getRole())
            .toString();
    }
}
