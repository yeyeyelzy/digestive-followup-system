package com.ruoyi.system.domain;

import org.apache.commons.lang3.builder.ToStringBuilder;
import org.apache.commons.lang3.builder.ToStringStyle;
import com.ruoyi.common.annotation.Excel;
import com.ruoyi.common.core.domain.BaseEntity;

/**
 * 医嘱管理对象 doctors_advice
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
public class DoctorsAdvice extends BaseEntity
{
    private static final long serialVersionUID = 1L;

    /** 医嘱id */
    private Long doctorsAdviceId;

    /** 患者姓名 */
    @Excel(name = "患者姓名")
    private String patientName;

    /** 用药方案 */
    @Excel(name = "用药方案")
    private String medicationRegimen;

    /** 复查计划 */
    @Excel(name = "复查计划")
    private String reviewPlan;

    /** 注意事项 */
    @Excel(name = "注意事项")
    private String notice;

    public void setDoctorsAdviceId(Long doctorsAdviceId) 
    {
        this.doctorsAdviceId = doctorsAdviceId;
    }

    public Long getDoctorsAdviceId() 
    {
        return doctorsAdviceId;
    }
    public void setPatientName(String patientName) 
    {
        this.patientName = patientName;
    }

    public String getPatientName() 
    {
        return patientName;
    }
    public void setMedicationRegimen(String medicationRegimen) 
    {
        this.medicationRegimen = medicationRegimen;
    }

    public String getMedicationRegimen() 
    {
        return medicationRegimen;
    }
    public void setReviewPlan(String reviewPlan) 
    {
        this.reviewPlan = reviewPlan;
    }

    public String getReviewPlan() 
    {
        return reviewPlan;
    }
    public void setNotice(String notice) 
    {
        this.notice = notice;
    }

    public String getNotice() 
    {
        return notice;
    }

    @Override
    public String toString() {
        return new ToStringBuilder(this,ToStringStyle.MULTI_LINE_STYLE)
            .append("doctorsAdviceId", getDoctorsAdviceId())
            .append("patientName", getPatientName())
            .append("medicationRegimen", getMedicationRegimen())
            .append("reviewPlan", getReviewPlan())
            .append("notice", getNotice())
            .toString();
    }
}
