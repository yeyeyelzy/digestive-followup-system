package com.ruoyi.system.domain;

import java.util.Date;
import com.fasterxml.jackson.annotation.JsonFormat;
import org.apache.commons.lang3.builder.ToStringBuilder;
import org.apache.commons.lang3.builder.ToStringStyle;
import com.ruoyi.common.annotation.Excel;
import com.ruoyi.common.core.domain.BaseEntity;

/**
 * 出院小结管理对象 discharge
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
public class Discharge extends BaseEntity
{
    private static final long serialVersionUID = 1L;

    /** 住院号 */
    private Integer admissionNumber;

    /** 患者id */
    @Excel(name = "患者id")
    private Long patientId;

    /** 患者姓名 */
    @Excel(name = "患者姓名")
    private String patientName;

    /** 入院时间 */
    @JsonFormat(pattern = "yyyy-MM-dd")
    @Excel(name = "入院时间", width = 30, dateFormat = "yyyy-MM-dd")
    private Date admissionDate;

    /** 出院时间 */
    @JsonFormat(pattern = "yyyy-MM-dd")
    @Excel(name = "出院时间", width = 30, dateFormat = "yyyy-MM-dd")
    private Date dischargeDate;

    /** 出院诊断 */
    @Excel(name = "出院诊断")
    private String dischargeDiagnosis;

    /** 主要化验结果 */
    @Excel(name = "主要化验结果")
    private String majorTestResult;

    /** 医嘱号 */
    @Excel(name = "医嘱号")
    private Long doctorsAdviceId;

    public void setAdmissionNumber(Integer admissionNumber) 
    {
        this.admissionNumber = admissionNumber;
    }

    public Integer getAdmissionNumber() 
    {
        return admissionNumber;
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
    public void setAdmissionDate(Date admissionDate) 
    {
        this.admissionDate = admissionDate;
    }

    public Date getAdmissionDate() 
    {
        return admissionDate;
    }
    public void setDischargeDate(Date dischargeDate) 
    {
        this.dischargeDate = dischargeDate;
    }

    public Date getDischargeDate() 
    {
        return dischargeDate;
    }
    public void setDischargeDiagnosis(String dischargeDiagnosis) 
    {
        this.dischargeDiagnosis = dischargeDiagnosis;
    }

    public String getDischargeDiagnosis() 
    {
        return dischargeDiagnosis;
    }
    public void setMajorTestResult(String majorTestResult) 
    {
        this.majorTestResult = majorTestResult;
    }

    public String getMajorTestResult() 
    {
        return majorTestResult;
    }
    public void setDoctorsAdviceId(Long doctorsAdviceId) 
    {
        this.doctorsAdviceId = doctorsAdviceId;
    }

    public Long getDoctorsAdviceId() 
    {
        return doctorsAdviceId;
    }

    @Override
    public String toString() {
        return new ToStringBuilder(this,ToStringStyle.MULTI_LINE_STYLE)
            .append("admissionNumber", getAdmissionNumber())
            .append("patientId", getPatientId())
            .append("patientName", getPatientName())
            .append("admissionDate", getAdmissionDate())
            .append("dischargeDate", getDischargeDate())
            .append("dischargeDiagnosis", getDischargeDiagnosis())
            .append("majorTestResult", getMajorTestResult())
            .append("doctorsAdviceId", getDoctorsAdviceId())
            .toString();
    }
}
