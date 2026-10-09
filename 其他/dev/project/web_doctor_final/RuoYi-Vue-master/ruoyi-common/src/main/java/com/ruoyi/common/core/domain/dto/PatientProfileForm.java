package com.ruoyi.common.core.domain.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import java.util.Date;

/**
 * 患者个人信息修改表单 DTO
 */
public class PatientProfileForm {

    private String phoneNumber;
    private Long gender; // 0=男, 1=女

    @JsonFormat(pattern = "yyyy-MM-dd")
    private Date birthday;

    private Double weight;

    private String avatarUrl;

    // --- Getter and Setter ---

    public String getPhoneNumber() {
        return phoneNumber;
    }

    public void setPhoneNumber(String phoneNumber) {
        this.phoneNumber = phoneNumber;
    }

    public Long getGender() {
        return gender;
    }

    public void setGender(Long gender) {
        this.gender = gender;
    }

    public Date getBirthday() {
        return birthday;
    }

    public void setBirthday(Date birthday) {
        this.birthday = birthday;
    }

    public Double getWeight() {
        return weight;
    }

    public void setWeight(Double weight) {
        this.weight = weight;
    }

    public String getAvatarUrl() {
        return avatarUrl;
    }

    public void setAvatarUrl(String avatarUrl) {
        this.avatarUrl = avatarUrl;
    }
}
