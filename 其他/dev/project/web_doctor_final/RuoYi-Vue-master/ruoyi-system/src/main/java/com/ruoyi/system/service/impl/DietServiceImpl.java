package com.ruoyi.system.service.impl;

import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.ruoyi.system.mapper.DietMapper;
import com.ruoyi.system.domain.Diet;
import com.ruoyi.system.service.IDietService;

/**
 * 饮食日记管理Service业务层处理
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
@Service
public class DietServiceImpl implements IDietService 
{
    @Autowired
    private DietMapper dietMapper;

    /**
     * 查询饮食日记管理
     * 
     * @param dietId 饮食日记管理主键
     * @return 饮食日记管理
     */
    @Override
    public Diet selectDietByDietId(Long dietId)
    {
        return dietMapper.selectDietByDietId(dietId);
    }

    /**
     * 查询饮食日记管理列表
     * 
     * @param diet 饮食日记管理
     * @return 饮食日记管理
     */
    @Override
    public List<Diet> selectDietList(Diet diet)
    {
        return dietMapper.selectDietList(diet);
    }

    /**
     * 查询饮食日记管理列表
     *
     * @param diet 饮食日记管理
     * @return 饮食日记管理
     */
    @Override
    public List<Diet> searchByIdDate(Diet diet)
    {
        return dietMapper.searchByIdDate(diet);
    }

    /**
     * 新增饮食日记管理
     * 
     * @param diet 饮食日记管理
     * @return 结果
     */
    @Override
    public int insertDiet(Diet diet)
    {
        return dietMapper.insertDiet(diet);
    }

    /**
     * 修改饮食日记管理
     * 
     * @param diet 饮食日记管理
     * @return 结果
     */
    @Override
    public int updateDiet(Diet diet)
    {
        return dietMapper.updateDiet(diet);
    }

    /**
     * 修改饮食日记管理
     *
     * @param diet 饮食日记管理
     * @return 结果
     */
    @Override
    public int updateIdDate(Diet diet)
    {
        return dietMapper.updateIdDate(diet);
    }

    /**
     * 批量删除饮食日记管理
     * 
     * @param dietIds 需要删除的饮食日记管理主键
     * @return 结果
     */
    @Override
    public int deleteDietByDietIds(Long[] dietIds)
    {
        return dietMapper.deleteDietByDietIds(dietIds);
    }

    /**
     * 删除饮食日记管理信息
     * 
     * @param dietId 饮食日记管理主键
     * @return 结果
     */
    @Override
    public int deleteDietByDietId(Long dietId)
    {
        return dietMapper.deleteDietByDietId(dietId);
    }
}
