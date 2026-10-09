package com.ruoyi.system.domain;

import java.util.Date;
import com.fasterxml.jackson.annotation.JsonFormat;
import org.apache.commons.lang3.builder.ToStringBuilder;
import org.apache.commons.lang3.builder.ToStringStyle;
import com.ruoyi.common.annotation.Excel;
import com.ruoyi.common.core.domain.BaseEntity;

/**
 * 随访记录管理对象 follow_up
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
public class FollowUp extends BaseEntity
{
    private static final long serialVersionUID = 1L;

    /** 随访记录id */
    private Long followUpId;

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

    /** 上次健康教育内容 */
    @Excel(name = "上次健康教育内容")
    private String lastHealthEducation;

    /** 自我报告 */
    @Excel(name = "自我报告")
    private String patientConclusion;

    /** 患者症状 */
    @Excel(name = "患者症状")
    private String patientSymptom;

    /** 患者压力 */
    @Excel(name = "患者压力")
    private String patientPressure;

    /** 患者照护者 */
    @Excel(name = "患者照护者")
    private String patientSupport;

    /** 临床治疗计划 */
    @Excel(name = "临床治疗计划")
    private String clinicalTreatmentPlan;

    /** 随访小结 */
    @Excel(name = "随访小结")
    private String summary;

    /** 当前主要护理诊断 */
    @Excel(name = "当前主要护理诊断")
    private String currentPrimaryCareDiagnosis;

    /** 健康指标情况 */
    @Excel(name = "健康指标情况")
    private String healthIndicator;

    /** 更新护理目标 */
    @Excel(name = "更新护理目标")
    private String newNursingGoal;

    /** 护理指导内容 */
    @Excel(name = "护理指导内容")
    private String guidance;

    /** 其他 */
    @Excel(name = "其他")
    private String note;

    public void setFollowUpId(Long followUpId) 
    {
        this.followUpId = followUpId;
    }

    public Long getFollowUpId() 
    {
        return followUpId;
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
    public void setLastHealthEducation(String lastHealthEducation) 
    {
        this.lastHealthEducation = lastHealthEducation;
    }

    public String getLastHealthEducation() 
    {
        return lastHealthEducation;
    }
    public void setPatientConclusion(String patientConclusion) 
    {
        this.patientConclusion = patientConclusion;
    }

    public String getPatientConclusion() 
    {
        return patientConclusion;
    }
    public void setPatientSymptom(String patientSymptom) 
    {
        this.patientSymptom = patientSymptom;
    }

    public String getPatientSymptom() 
    {
        return patientSymptom;
    }
    public void setPatientPressure(String patientPressure) 
    {
        this.patientPressure = patientPressure;
    }

    public String getPatientPressure() 
    {
        return patientPressure;
    }
    public void setPatientSupport(String patientSupport) 
    {
        this.patientSupport = patientSupport;
    }

    public String getPatientSupport() 
    {
        return patientSupport;
    }
    public void setClinicalTreatmentPlan(String clinicalTreatmentPlan) 
    {
        this.clinicalTreatmentPlan = clinicalTreatmentPlan;
    }

    public String getClinicalTreatmentPlan() 
    {
        return clinicalTreatmentPlan;
    }
    public void setSummary(String summary) 
    {
        this.summary = summary;
    }

    public String getSummary() 
    {
        return summary;
    }
    public void setCurrentPrimaryCareDiagnosis(String currentPrimaryCareDiagnosis) 
    {
        this.currentPrimaryCareDiagnosis = currentPrimaryCareDiagnosis;
    }

    public String getCurrentPrimaryCareDiagnosis() 
    {
        return currentPrimaryCareDiagnosis;
    }
    public void setHealthIndicator(String healthIndicator) 
    {
        this.healthIndicator = healthIndicator;
    }

    public String getHealthIndicator() 
    {
        return healthIndicator;
    }
    public void setNewNursingGoal(String newNursingGoal) 
    {
        this.newNursingGoal = newNursingGoal;
    }

    public String getNewNursingGoal() 
    {
        return newNursingGoal;
    }
    public void setGuidance(String guidance) 
    {
        this.guidance = guidance;
    }

    public String getGuidance() 
    {
        return guidance;
    }
    public void setNote(String note) 
    {
        this.note = note;
    }

    public String getNote() 
    {
        return note;
    }

    @Override
    public String toString() {
        return new ToStringBuilder(this,ToStringStyle.MULTI_LINE_STYLE)
            .append("followUpId", getFollowUpId())
            .append("patientId", getPatientId())
            .append("patientName", getPatientName())
            .append("date", getDate())
            .append("lastHealthEducation", getLastHealthEducation())
            .append("patientConclusion", getPatientConclusion())
            .append("patientSymptom", getPatientSymptom())
            .append("patientPressure", getPatientPressure())
            .append("patientSupport", getPatientSupport())
            .append("clinicalTreatmentPlan", getClinicalTreatmentPlan())
            .append("summary", getSummary())
            .append("currentPrimaryCareDiagnosis", getCurrentPrimaryCareDiagnosis())
            .append("healthIndicator", getHealthIndicator())
            .append("newNursingGoal", getNewNursingGoal())
            .append("guidance", getGuidance())
            .append("note", getNote())
            .toString();
    }
}
