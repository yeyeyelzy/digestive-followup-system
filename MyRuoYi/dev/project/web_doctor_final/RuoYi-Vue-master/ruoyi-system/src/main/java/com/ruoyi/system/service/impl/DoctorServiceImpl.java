package com.ruoyi.system.service.impl;

import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.ruoyi.system.mapper.DoctorMapper;
import com.ruoyi.system.domain.Doctor;
import com.ruoyi.system.service.IDoctorService;

/**
 * 医生管理Service业务层处理
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
@Service
public class DoctorServiceImpl implements IDoctorService 
{
    @Autowired
    private DoctorMapper doctorMapper;

    /**
     * 查询医生管理
     * 
     * @param doctorId 医生管理主键
     * @return 医生管理
     */
    @Override
    public Doctor selectDoctorByDoctorId(Long doctorId)
    {
        return doctorMapper.selectDoctorByDoctorId(doctorId);
    }

    /**
     * 查询医生管理列表
     * 
     * @param doctor 医生管理
     * @return 医生管理
     */
    @Override
    public List<Doctor> selectDoctorList(Doctor doctor)
    {
        return doctorMapper.selectDoctorList(doctor);
    }

    /**
     * 新增医生管理
     * 
     * @param doctor 医生管理
     * @return 结果
     */
    @Override
    public int insertDoctor(Doctor doctor)
    {
        return doctorMapper.insertDoctor(doctor);
    }

    /**
     * 修改医生管理
     * 
     * @param doctor 医生管理
     * @return 结果
     */
    @Override
    public int updateDoctor(Doctor doctor)
    {
        return doctorMapper.updateDoctor(doctor);
    }

    /**
     * 批量删除医生管理
     * 
     * @param doctorIds 需要删除的医生管理主键
     * @return 结果
     */
    @Override
    public int deleteDoctorByDoctorIds(Long[] doctorIds)
    {
        return doctorMapper.deleteDoctorByDoctorIds(doctorIds);
    }

    /**
     * 删除医生管理信息
     * 
     * @param doctorId 医生管理主键
     * @return 结果
     */
    @Override
    public int deleteDoctorByDoctorId(Long doctorId)
    {
        return doctorMapper.deleteDoctorByDoctorId(doctorId);
    }
}
