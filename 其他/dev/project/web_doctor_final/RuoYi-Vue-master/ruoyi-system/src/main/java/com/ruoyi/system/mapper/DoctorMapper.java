package com.ruoyi.system.mapper;

import java.util.List;
import com.ruoyi.system.domain.Doctor;

/**
 * 医生管理Mapper接口
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
public interface DoctorMapper 
{
    /**
     * 查询医生管理
     * 
     * @param doctorId 医生管理主键
     * @return 医生管理
     */
    public Doctor selectDoctorByDoctorId(Long doctorId);

    /**
     * 查询医生管理
     *
     * @param doctorName 医生管理姓名
     * @return 医生管理
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
     * 删除医生管理
     * 
     * @param doctorId 医生管理主键
     * @return 结果
     */
    public int deleteDoctorByDoctorId(Long doctorId);

    /**
     * 批量删除医生管理
     * 
     * @param doctorIds 需要删除的数据主键集合
     * @return 结果
     */
    public int deleteDoctorByDoctorIds(Long[] doctorIds);
}
