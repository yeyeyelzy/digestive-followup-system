package com.ruoyi.system.domain;

import java.util.Date;
import com.fasterxml.jackson.annotation.JsonFormat;
import org.apache.commons.lang3.builder.ToStringBuilder;
import org.apache.commons.lang3.builder.ToStringStyle;
import com.ruoyi.common.annotation.Excel;
import com.ruoyi.common.core.domain.BaseEntity;

/**
 * 行为日记管理对象 behavior
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
public class Behavior extends BaseEntity
{
    private static final long serialVersionUID = 1L;

    /** 行为日记id */
    private Long behaviorId;

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

    /** 频率 */
    @Excel(name = "频率")
    private Long frequency;

    /** 分级 */
    @Excel(name = "分级")
    private Long strength;

    /** 时长 */
    @Excel(name = "时长")
    private Long duration;

    /** 类型（枚举，或规定有氧无氧，简单处理） */
    @Excel(name = "类型", readConverterExp = "枚=举，或规定有氧无氧，简单处理")
    private Long type;

    /** 感受 */
    @Excel(name = "感受")
    private String feel;

    /** 每周复盘 */
    @Excel(name = "每周复盘")
    private String replay;

    /** 运动管理问题 */
    @Excel(name = "运动管理问题")
    private String question;

    public void setBehaviorId(Long behaviorId) 
    {
        this.behaviorId = behaviorId;
    }

    public Long getBehaviorId() 
    {
        return behaviorId;
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
    public void setFrequency(Long frequency) 
    {
        this.frequency = frequency;
    }

    public Long getFrequency() 
    {
        return frequency;
    }
    public void setStrength(Long strength) 
    {
        this.strength = strength;
    }

    public Long getStrength() 
    {
        return strength;
    }
    public void setDuration(Long duration) 
    {
        this.duration = duration;
    }

    public Long getDuration() 
    {
        return duration;
    }
    public void setType(Long type) 
    {
        this.type = type;
    }

    public Long getType() 
    {
        return type;
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
    public void setQuestion(String question) 
    {
        this.question = question;
    }

    public String getQuestion() 
    {
        return question;
    }

    @Override
    public String toString() {
        return new ToStringBuilder(this,ToStringStyle.MULTI_LINE_STYLE)
            .append("behaviorId", getBehaviorId())
            .append("patientId", getPatientId())
            .append("patientName", getPatientName())
            .append("date", getDate())
            .append("frequency", getFrequency())
            .append("strength", getStrength())
            .append("duration", getDuration())
            .append("type", getType())
            .append("feel", getFeel())
            .append("replay", getReplay())
            .append("question", getQuestion())
            .toString();
    }
}
