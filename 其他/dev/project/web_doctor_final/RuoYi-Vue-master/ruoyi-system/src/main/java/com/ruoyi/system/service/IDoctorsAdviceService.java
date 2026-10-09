package com.ruoyi.system.service;

import java.util.List;
import com.ruoyi.system.domain.DoctorsAdvice;

/**
 * 医嘱管理Service接口
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
public interface IDoctorsAdviceService 
{
    /**
     * 查询医嘱管理
     * 
     * @param doctorsAdviceId 医嘱管理主键
     * @return 医嘱管理
     */
    public DoctorsAdvice selectDoctorsAdviceByDoctorsAdviceId(Long doctorsAdviceId);

    /**
     * 查询医嘱管理列表
     * 
     * @param doctorsAdvice 医嘱管理
     * @return 医嘱管理集合
     */
    public List<DoctorsAdvice> selectDoctorsAdviceList(DoctorsAdvice doctorsAdvice);

    /**
     * 新增医嘱管理
     * 
     * @param doctorsAdvice 医嘱管理
     * @return 结果
     */
    public int insertDoctorsAdvice(DoctorsAdvice doctorsAdvice);

    /**
     * 修改医嘱管理
     * 
     * @param doctorsAdvice 医嘱管理
     * @return 结果
     */
    public int updateDoctorsAdvice(DoctorsAdvice doctorsAdvice);

    /**
     * 批量删除医嘱管理
     * 
     * @param doctorsAdviceIds 需要删除的医嘱管理主键集合
     * @return 结果
     */
    public int deleteDoctorsAdviceByDoctorsAdviceIds(Long[] doctorsAdviceIds);

    /**
     * 删除医嘱管理信息
     * 
     * @param doctorsAdviceId 医嘱管理主键
     * @return 结果
     */
    public int deleteDoctorsAdviceByDoctorsAdviceId(Long doctorsAdviceId);
}
