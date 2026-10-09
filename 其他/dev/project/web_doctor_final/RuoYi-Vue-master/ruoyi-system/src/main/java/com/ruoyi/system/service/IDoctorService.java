package com.ruoyi.system.service;

import java.util.List;
import com.ruoyi.system.domain.Doctor;

/**
 * 医生管理Service接口
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
public interface IDoctorService 
{
    /**
     * 查询医生管理
     * 
     * @param doctorId 医生管理主键
     * @return 医生管理
     */
    public Doctor selectDoctorByDoctorId(Long doctorId);

    /**
     * 根据医生姓名查询医生信息
     * @param doctorName 医生姓名
     * @return 医生信息
     */
    public Doctor selectDoctorByDoctorName(String doctorName);

    /**
     * 查询医生管理列表
     * 
     * @param doctor 医生管理
     * @return 医生管理集合
     */
    public List<Doctor> selectDoctorList(Doctor doctor);

    /**
     * 新增医生管理
     * 
     * @param doctor 医生管理
     * @return 结果
     */
    public int insertDoctor(Doctor doctor);

    /**
     * 修改医生管理
     * 
     * @param doctor 医生管理
     * @return 结果
     */
    public int updateDoctor(Doctor doctor);

    /**
     * 批量删除医生管理
     * 
     * @param doctorIds 需要删除的医生管理主键集合
     * @return 结果
     */
    public int deleteDoctorByDoctorIds(Long[] doctorIds);

    /**
     * 删除医生管理信息
     * 
     * @param doctorId 医生管理主键
     * @return 结果
     */
    public int deleteDoctorByDoctorId(Long doctorId);
}
