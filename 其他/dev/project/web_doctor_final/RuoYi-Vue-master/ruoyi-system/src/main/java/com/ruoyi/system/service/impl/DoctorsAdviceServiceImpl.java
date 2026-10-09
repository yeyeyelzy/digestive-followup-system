package com.ruoyi.system.service.impl;

import java.util.List;

import com.ruoyi.common.annotation.DataScope;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.ruoyi.system.mapper.DoctorsAdviceMapper;
import com.ruoyi.system.domain.DoctorsAdvice;
import com.ruoyi.system.service.IDoctorsAdviceService;

/**
 * 医嘱管理Service业务层处理
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
@Service
public class DoctorsAdviceServiceImpl implements IDoctorsAdviceService 
{
    @Autowired
    private DoctorsAdviceMapper doctorsAdviceMapper;

    /**
     * 查询医嘱管理
     * 
     * @param doctorsAdviceId 医嘱管理主键
     * @return 医嘱管理
     */
    @Override
    public DoctorsAdvice selectDoctorsAdviceByDoctorsAdviceId(Long doctorsAdviceId)
    {
        return doctorsAdviceMapper.selectDoctorsAdviceByDoctorsAdviceId(doctorsAdviceId);
    }

    /**
     * 查询医嘱管理列表
     * 
     * @param doctorsAdvice 医嘱管理
     * @return 医嘱管理
     */
    @Override
    public List<DoctorsAdvice> selectDoctorsAdviceList(DoctorsAdvice doctorsAdvice)
    {
        return doctorsAdviceMapper.selectDoctorsAdviceList(doctorsAdvice);
    }

    /**
     * 新增医嘱管理
     * 
     * @param doctorsAdvice 医嘱管理
     * @return 结果
     */
    @Override
    public int insertDoctorsAdvice(DoctorsAdvice doctorsAdvice)
    {
        return doctorsAdviceMapper.insertDoctorsAdvice(doctorsAdvice);
    }

    /**
     * 修改医嘱管理
     * 
     * @param doctorsAdvice 医嘱管理
     * @return 结果
     */
    @Override
    public int updateDoctorsAdvice(DoctorsAdvice doctorsAdvice)
    {
        return doctorsAdviceMapper.updateDoctorsAdvice(doctorsAdvice);
    }

    /**
     * 批量删除医嘱管理
     * 
     * @param doctorsAdviceIds 需要删除的医嘱管理主键
     * @return 结果
     */
    @Override
    public int deleteDoctorsAdviceByDoctorsAdviceIds(Long[] doctorsAdviceIds)
    {
        return doctorsAdviceMapper.deleteDoctorsAdviceByDoctorsAdviceIds(doctorsAdviceIds);
    }

    /**
     * 删除医嘱管理信息
     * 
     * @param doctorsAdviceId 医嘱管理主键
     * @return 结果
     */
    @Override
    public int deleteDoctorsAdviceByDoctorsAdviceId(Long doctorsAdviceId)
    {
        return doctorsAdviceMapper.deleteDoctorsAdviceByDoctorsAdviceId(doctorsAdviceId);
    }
}
