package com.ruoyi.system.domain;

import java.util.Date;
import com.fasterxml.jackson.annotation.JsonFormat;
import org.apache.commons.lang3.builder.ToStringBuilder;
import org.apache.commons.lang3.builder.ToStringStyle;
import com.ruoyi.common.annotation.Excel;
import com.ruoyi.common.core.domain.BaseEntity;

/**
 * 饮食日记管理对象 diet
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
public class Diet extends BaseEntity
{
    private static final long serialVersionUID = 1L;

    /** 饮食日记id */
    private Long dietId;

    /** 患者id */
    @Excel(name = "患者id")
    private Long patientId;

    /** 患者姓名 */
    @Excel(name = "患者姓名")
    private String patientName;

    /** 日期 */
    @JsonFormat(pattern = "yyyy-MM-dd")
    @Excel(name = "日期", width = 30, dateFormat = "yyyy-MM-dd")
    private Date date;

    /** 饮食描述 */
    @Excel(name = "饮食描述")
    private String dietDescription;

    /** 饮食照片 */
    @Excel(name = "饮食照片")
    private String dietPictureUrl;

    /** 卡路里 */
    @Excel(name = "卡路里")
    private Long kcal;

    /** 感受 */
    @Excel(name = "感受")
    private String feel;

    /** 每周复盘 */
    @Excel(name = "每周复盘")
    private String replay;

    /** 饮食困惑 */
    @Excel(name = "饮食困惑")
    private String confusion;

    public void setDietId(Long dietId) 
    {
        this.dietId = dietId;
    }

    public Long getDietId() 
    {
        return dietId;
    }
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
    public void setDate(Date date) 
    {
        this.date = date;
    }

    public Date getDate() 
    {
        return date;
    }
    public void setDietDescription(String dietDescription) 
    {
        this.dietDescription = dietDescription;
    }

    public String getDietDescription() 
    {
        return dietDescription;
    }
    public void setDietPictureUrl(String dietPictureUrl) 
    {
        this.dietPictureUrl = dietPictureUrl;
    }

    public String getDietPictureUrl() 
    {
        return dietPictureUrl;
    }
    public void setKcal(Long kcal) 
    {
        this.kcal = kcal;
    }

    public Long getKcal() 
    {
        return kcal;
    }
    public void setFeel(String feel) 
    {
        this.feel = feel;
    }

    public String getFeel() 
    {
        return feel;
    }
    public void setReplay(String replay) 
    {
        this.replay = replay;
    }

    public String getReplay() 
    {
        return replay;
    }
    public void setConfusion(String confusion) 
    {
        this.confusion = confusion;
    }

    public String getConfusion() 
    {
        return confusion;
    }

    @Override
    public String toString() {
        return new ToStringBuilder(this,ToStringStyle.MULTI_LINE_STYLE)
            .append("dietId", getDietId())
            .append("patientId", getPatientId())
            .append("patientName", getPatientName())
            .append("date", getDate())
            .append("dietDescription", getDietDescription())
            .append("dietPictureUrl", getDietPictureUrl())
            .append("kcal", getKcal())
            .append("feel", getFeel())
            .append("replay", getReplay())
            .append("confusion", getConfusion())
            .toString();
    }
}
