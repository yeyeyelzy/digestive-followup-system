package com.ruoyi.system.domain;

import java.util.Date;
import com.fasterxml.jackson.annotation.JsonFormat;
import org.apache.commons.lang3.builder.ToStringBuilder;
import org.apache.commons.lang3.builder.ToStringStyle;
import com.ruoyi.common.annotation.Excel;
import com.ruoyi.common.core.domain.BaseEntity;

/**
 * 生活方式日记管理对象 living
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
public class Living extends BaseEntity
{
    private static final long serialVersionUID = 1L;

    /** 生活日记id */
    private Long livingId;

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

    /** 需要改变的生活方式 */
    @Excel(name = "需要改变的生活方式")
    private String neededChange;

    /** 是否改善 */
    @Excel(name = "是否改善")
    private Long isImproved;

    /** 感受 */
    @Excel(name = "感受")
    private String feel;

    /** 问题 */
    @Excel(name = "问题")
    private String question;

    public void setLivingId(Long livingId) 
    {
        this.livingId = livingId;
    }

    public Long getLivingId() 
    {
        return livingId;
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
    public void setNeededChange(String neededChange) 
    {
        this.neededChange = neededChange;
    }

    public String getNeededChange() 
    {
        return neededChange;
    }
    public void setIsImproved(Long isImproved) 
    {
        this.isImproved = isImproved;
    }

    public Long getIsImproved() 
    {
        return isImproved;
    }
    public void setFeel(String feel) 
    {
        this.feel = feel;
    }

    public String getFeel() 
    {
        return feel;
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
            .append("livingId", getLivingId())
            .append("patientId", getPatientId())
            .append("patientName", getPatientName())
            .append("date", getDate())
            .append("neededChange", getNeededChange())
            .append("isImproved", getIsImproved())
            .append("feel", getFeel())
            .append("question", getQuestion())
            .toString();
    }
}
