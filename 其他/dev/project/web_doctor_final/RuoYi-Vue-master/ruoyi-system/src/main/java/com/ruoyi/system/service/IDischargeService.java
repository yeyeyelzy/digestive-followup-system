package com.ruoyi.system.service;

import java.util.List;
import com.ruoyi.system.domain.Discharge;

/**
 * 出院小结管理Service接口
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
public interface IDischargeService 
{
    /**
     * 查询出院小结管理
     * 
     * @param admissionNumber 出院小结管理主键
     * @return 出院小结管理
     */
    public Discharge selectDischargeByAdmissionNumber(Integer admissionNumber);

    /**
     * 查询出院小结管理列表
     * 
     * @param discharge 出院小结管理
     * @return 出院小结管理集合
     */
    public List<Discharge> selectDischargeList(Discharge discharge);

    /**
     * 新增出院小结管理
     * 
     * @param discharge 出院小结管理
     * @return 结果
     */
    public int insertDischarge(Discharge discharge);

    /**
     * 修改出院小结管理
     * 
     * @param discharge 出院小结管理
     * @return 结果
     */
    public int updateDischarge(Discharge discharge);

    /**
     * 批量删除出院小结管理
     * 
     * @param admissionNumbers 需要删除的出院小结管理主键集合
     * @return 结果
     */
    public int deleteDischargeByAdmissionNumbers(Integer[] admissionNumbers);

    /**
     * 删除出院小结管理信息
     * 
     * @param admissionNumber 出院小结管理主键
     * @return 结果
     */
    public int deleteDischargeByAdmissionNumber(Integer admissionNumber);
}
