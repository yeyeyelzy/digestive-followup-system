package com.ruoyi.system.domain;

import java.util.Date;
import com.fasterxml.jackson.annotation.JsonFormat;
import org.apache.commons.lang3.builder.ToStringBuilder;
import org.apache.commons.lang3.builder.ToStringStyle;
import com.ruoyi.common.annotation.Excel;
import com.ruoyi.common.core.domain.BaseEntity;

/**
 * 聊天记录管理对象 chat
 *
 * @author ruoyi
 * @date 2023-07-11
 */

public class ScienceChat extends BaseEntity
{
    private static final long serialVersionUID = 1L;

    /** 聊天id */
    private Long id;

    /** 患者id */
    @Excel(name = "患者id")
    private Long patientId;

    /** 患者姓名 */
    @Excel(name = "患者姓名")
    private String patientName;


    /** 聊天内容 */
    @Excel(name = "聊天内容")
    private String content;

    /** 聊天时间 */
    @JsonFormat(pattern = "YYYY-MM-dd hh:mm:ss")
    @Excel(name = "聊天时间", width = 30, dateFormat = "YYYY-MM-dd hh:mm:ss")
    private Date time;

    /** 发送方向 */
    @Excel(name = "发送方向")
    private Long direction;

    public void setId(Long id)
    {
        this.id = id;
    }

    public Long getId()
    {
        return id;
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

    public String getContent()
    {
        return content;
    }
    public void setTime(Date time)
    {
        this.time = time;
    }

    public Date getTime()
    {
        return time;
    }

    public Long getDirection() {
        return direction;
    }

    public void setDirection(Long direction) {
        this.direction = direction;
    }

    @Override
    public String toString() {
        return new ToStringBuilder(this,ToStringStyle.MULTI_LINE_STYLE)
                .append("id", getId())
                .append("patientId", getPatientId())
                .append("patientName", getPatientName())
                .append("content", getContent())
                .append("time", getTime())
                .append("direction", getDirection())
                .toString();
    }
}
