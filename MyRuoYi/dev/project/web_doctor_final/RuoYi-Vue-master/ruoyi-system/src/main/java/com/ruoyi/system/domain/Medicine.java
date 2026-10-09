package com.ruoyi.system.domain;

import java.util.Date;
import com.fasterxml.jackson.annotation.JsonFormat;
import org.apache.commons.lang3.builder.ToStringBuilder;
import org.apache.commons.lang3.builder.ToStringStyle;
import com.ruoyi.common.annotation.Excel;
import com.ruoyi.common.core.domain.BaseEntity;

/**
 * 服药日记管理对象 medicine
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
public class Medicine extends BaseEntity
{
    private static final long serialVersionUID = 1L;

    /** 用药日记id */
    private Long medicineId;

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

    /** 是否服药 */
    @Excel(name = "是否服药")
    private Long flag;

    /** 症状（枚举） */
    @Excel(name = "症状", readConverterExp = "枚=举")
    private Long symptom;

    /** 复盘 */
    @Excel(name = "复盘")
    private String replay;

    /** 服药管理问题 */
    @Excel(name = "服药管理问题")
    private String question;

    public void setMedicineId(Long medicineId) 
    {
        this.medicineId = medicineId;
    }

    public Long getMedicineId() 
    {
        return medicineId;
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
    public void setFlag(Long flag) 
    {
        this.flag = flag;
    }

    public Long getFlag() 
    {
        return flag;
    }
    public void setSymptom(Long symptom) 
    {
        this.symptom = symptom;
    }

    public Long getSymptom() 
    {
        return symptom;
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
            .append("medicineId", getMedicineId())
            .append("patientId", getPatientId())
            .append("patientName", getPatientName())
            .append("date", getDate())
            .append("flag", getFlag())
            .append("symptom", getSymptom())
            .append("replay", getReplay())
            .append("question", getQuestion())
            .toString();
    }
}
