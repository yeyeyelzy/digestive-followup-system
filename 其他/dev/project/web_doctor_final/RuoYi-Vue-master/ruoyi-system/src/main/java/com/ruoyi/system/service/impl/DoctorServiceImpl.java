package com.ruoyi.system.service.impl;

import java.util.List;

import com.ruoyi.common.core.domain.entity.SysUser;
import com.ruoyi.common.exception.ServiceException;
import com.ruoyi.common.utils.StringUtils;
import com.ruoyi.system.service.ISysUserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.ruoyi.system.mapper.DoctorMapper;
import com.ruoyi.system.domain.Doctor;
import com.ruoyi.system.service.IDoctorService;
import org.springframework.transaction.annotation.Transactional;

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

    @Autowired
    private ISysUserService  userService;
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
     * 查询医生管理
     *
     * @param doctorName 医生管理姓名
     * @return 医生管理
     */
    @Override
    public Doctor selectDoctorByDoctorName(String doctorName){return doctorMapper.selectDoctorByDoctorName(doctorName);}

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
    @Transactional(rollbackFor = Exception.class) // 参考 SysUserServiceImpl 的事务注解，保证原子性
    public int deleteDoctorByDoctorIds(Long[] doctorIds) {

        // 2. 遍历医生ID，通过 doctor_name 关联用户，调用你已有的 userService 删除用户
        for (Long doctorId : doctorIds) {
            Doctor doctor = selectDoctorByDoctorId(doctorId);
            if (doctor == null || StringUtils.isEmpty(doctor.getDoctorName())) {
                throw new ServiceException("医生[" + doctorId + "]关联信息缺失，删除中断");
            }

            // 调用你已有的 selectUserByUserName 方法，通过 doctor_name 查用户
            SysUser user = userService.selectUserByUserName(doctor.getDoctorName());
            if (user != null) {
                userService.deleteUserByIds(new Long[]{user.getUserId()});
            }
        }

        int doctorDeleteCount = doctorMapper.deleteDoctorByDoctorIds(doctorIds);
        if (doctorDeleteCount == 0) {
            throw new ServiceException("医生数据不存在，删除失败");
        }

        return doctorDeleteCount;
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
