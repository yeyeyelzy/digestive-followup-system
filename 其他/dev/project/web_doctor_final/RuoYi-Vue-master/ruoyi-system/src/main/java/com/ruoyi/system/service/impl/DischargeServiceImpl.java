package com.ruoyi.system.service.impl;

import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.ruoyi.system.mapper.DischargeMapper;
import com.ruoyi.system.domain.Discharge;
import com.ruoyi.system.service.IDischargeService;

/**
 * 出院小结管理Service业务层处理
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
@Service
public class DischargeServiceImpl implements IDischargeService 
{
    @Autowired
    private DischargeMapper dischargeMapper;

    /**
     * 查询出院小结管理
     * 
     * @param admissionNumber 出院小结管理主键
     * @return 出院小结管理
     */
    @Override
    public Discharge selectDischargeByAdmissionNumber(Integer admissionNumber)
    {
        return dischargeMapper.selectDischargeByAdmissionNumber(admissionNumber);
    }

    /**
     * 查询出院小结管理列表
     * 
     * @param discharge 出院小结管理
     * @return 出院小结管理
     */
    @Override
    public List<Discharge> selectDischargeList(Discharge discharge)
    {
        return dischargeMapper.selectDischargeList(discharge);
    }

    /**
     * 新增出院小结管理
     * 
     * @param discharge 出院小结管理
     * @return 结果
     */
    @Override
    public int insertDischarge(Discharge discharge)
    {
        return dischargeMapper.insertDischarge(discharge);
    }

    /**
     * 修改出院小结管理
     * 
     * @param discharge 出院小结管理
     * @return 结果
     */
    @Override
    public int updateDischarge(Discharge discharge)
    {
        return dischargeMapper.updateDischarge(discharge);
    }

    /**
     * 批量删除出院小结管理
     * 
     * @param admissionNumbers 需要删除的出院小结管理主键
     * @return 结果
     */
    @Override
    public int deleteDischargeByAdmissionNumbers(Integer[] admissionNumbers)
    {
        return dischargeMapper.deleteDischargeByAdmissionNumbers(admissionNumbers);
    }

    /**
     * 删除出院小结管理信息
     * 
     * @param admissionNumber 出院小结管理主键
     * @return 结果
     */
    @Override
    public int deleteDischargeByAdmissionNumber(Integer admissionNumber)
    {
        return dischargeMapper.deleteDischargeByAdmissionNumber(admissionNumber);
    }
}
