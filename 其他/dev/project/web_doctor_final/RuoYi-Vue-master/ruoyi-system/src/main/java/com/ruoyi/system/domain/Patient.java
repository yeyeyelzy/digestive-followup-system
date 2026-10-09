package com.ruoyi.system.domain;

import org.apache.commons.lang3.builder.ToStringBuilder;
import org.apache.commons.lang3.builder.ToStringStyle;
import com.ruoyi.common.annotation.Excel;
import com.ruoyi.common.core.domain.BaseEntity;

/**
 * 患者管理对象 patient
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
public class Patient extends BaseEntity
{
    private static final long serialVersionUID = 1L;

    /** 患者id */
    private Long patientId;

    /** 患者姓名 */
    @Excel(name = "患者姓名")
    private String patientName;

    /** 头像 */
    @Excel(name = "头像")
    private String avatarUrl;

    /** 电话 */
    @Excel(name = "电话")
    private String phoneNumber;

    /** 年龄 */
    @Excel(name = "年龄")
    private Long age;

    /** 性别 */
    @Excel(name = "性别")
    private Long gender;

    /** 体重 */
    @Excel(name = "体重")
    private double weight;

    public void setPatientId(Long patientId) 
    {
        this.patientId = patientId;
    }

    public Long getPatientId() 
    {
        return patientId;
    }
    public void setPatientName(String patientName) 
    {
        this.patientName = patientName;
    }

    public String getPatientName() 
    {
        return patientName;
    }
    public void setAvatarUrl(String avatarUrl) 
    {
        this.avatarUrl = avatarUrl;
    }

    public String getAvatarUrl() 
    {
        return avatarUrl;
    }
    public void setPhoneNumber(String phoneNumber) 
    {
        this.phoneNumber = phoneNumber;
    }

    public String getPhoneNumber() 
    {
        return phoneNumber;
    }
    public void setAge(Long age)
    {
        this.age = age;
    }

    public Long getAge()
    {
        return age;
    }
    public void setGender(Long gender)
    {
        this.gender = gender;
    }

    public Long getGender()
    {
        return gender;
    }
    public void setWeight(double weight)
    {
        this.weight = weight;
    }

    public double getWeight()
    {
        return weight;
    }

    @Override
    public String toString() {
        return new ToStringBuilder(this,ToStringStyle.MULTI_LINE_STYLE)
            .append("patientId", getPatientId())
            .append("patientName", getPatientName())
            .append("avatarUrl", getAvatarUrl())
            .append("phoneNumber", getPhoneNumber())
            .append("age", getAge())
            .append("gender", getGender())
            .append("weight", getWeight())
            .toString();
    }
}
