package com.ruoyi.system.domain;

import java.util.Date;
import com.fasterxml.jackson.annotation.JsonFormat;
import org.apache.commons.lang3.builder.ToStringBuilder;
import org.apache.commons.lang3.builder.ToStringStyle;
import com.ruoyi.common.annotation.Excel;
import com.ruoyi.common.core.domain.BaseEntity;

/**
 * 复查管理对象 recovery
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
public class Recovery extends BaseEntity
{
    private static final long serialVersionUID = 1L;

    /** 复查id */
    private Long recoveryId;

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

    /** NT_proBNP */
    @Excel(name = "NT_proBNP")
    private Long ntProbnp;

    /** LVEF */
    @Excel(name = "LVEF")
    private Long LVEF;

    /** 峰值公斤摄氧量 */
    @Excel(name = "峰值公斤摄氧量")
    private Long CPET1;

    /** 无氧公斤摄氧量 */
    @Excel(name = "无氧公斤摄氧量")
    private Long CPET2;

    /** 峰值血压 */
    @Excel(name = "峰值血压")
    private Long peakBloodPressure;

    /** 峰值心率 */
    @Excel(name = "峰值心率")
    private Long peakHeartRate;

    /** 无氧阈血压 */
    @Excel(name = "无氧阈血压")
    private Long anaerobicThresholdBloodPressure;

    /** 无氧阈心率 */
    @Excel(name = "无氧阈心率")
    private Long anaerobicThresholdHeartRate;

    public void setRecoveryId(Long recoveryId) 
    {
        this.recoveryId = recoveryId;
    }

    public Long getRecoveryId() 
    {
        return recoveryId;
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
    public void setNtProbnp(Long ntProbnp) 
    {
        this.ntProbnp = ntProbnp;
    }

    public Long getNtProbnp() 
    {
        return ntProbnp;
    }
    public void setLVEF(Long LVEF) 
    {
        this.LVEF = LVEF;
    }

    public Long getLVEF() 
    {
        return LVEF;
    }
    public void setCPET1(Long CPET1) 
    {
        this.CPET1 = CPET1;
    }

    public Long getCPET1() 
    {
        return CPET1;
    }
    public void setCPET2(Long CPET2) 
    {
        this.CPET2 = CPET2;
    }

    public Long getCPET2() 
    {
        return CPET2;
    }
    public void setPeakBloodPressure(Long peakBloodPressure) 
    {
        this.peakBloodPressure = peakBloodPressure;
    }

    public Long getPeakBloodPressure() 
    {
        return peakBloodPressure;
    }
    public void setPeakHeartRate(Long peakHeartRate) 
    {
        this.peakHeartRate = peakHeartRate;
    }

    public Long getPeakHeartRate() 
    {
        return peakHeartRate;
    }
    public void setAnaerobicThresholdBloodPressure(Long anaerobicThresholdBloodPressure) 
    {
        this.anaerobicThresholdBloodPressure = anaerobicThresholdBloodPressure;
    }

    public Long getAnaerobicThresholdBloodPressure() 
    {
        return anaerobicThresholdBloodPressure;
    }
    public void setAnaerobicThresholdHeartRate(Long anaerobicThresholdHeartRate) 
    {
        this.anaerobicThresholdHeartRate = anaerobicThresholdHeartRate;
    }

    public Long getAnaerobicThresholdHeartRate() 
    {
        return anaerobicThresholdHeartRate;
    }

    @Override
    public String toString() {
        return new ToStringBuilder(this,ToStringStyle.MULTI_LINE_STYLE)
            .append("recoveryId", getRecoveryId())
            .append("patientId", getPatientId())
            .append("patientName", getPatientName())
            .append("date", getDate())
            .append("ntProbnp", getNtProbnp())
            .append("LVEF", getLVEF())
            .append("CPET1", getCPET1())
            .append("CPET2", getCPET2())
            .append("peakBloodPressure", getPeakBloodPressure())
            .append("peakHeartRate", getPeakHeartRate())
            .append("anaerobicThresholdBloodPressure", getAnaerobicThresholdBloodPressure())
            .append("anaerobicThresholdHeartRate", getAnaerobicThresholdHeartRate())
            .toString();
    }
}
