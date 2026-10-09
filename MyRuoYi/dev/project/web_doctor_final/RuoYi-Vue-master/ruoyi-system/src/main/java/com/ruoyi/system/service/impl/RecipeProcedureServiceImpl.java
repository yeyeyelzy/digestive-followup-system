package com.ruoyi.system.service.impl;

import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.ruoyi.system.mapper.RecipeProcedureMapper;
import com.ruoyi.system.domain.RecipeProcedure;
import com.ruoyi.system.service.IRecipeProcedureService;

/**
 * 【请填写功能名称】Service业务层处理
 * 
 * @author ruoyi
 * @date 2023-07-14
 */
@Service
public class RecipeProcedureServiceImpl implements IRecipeProcedureService 
{
    @Autowired
    private RecipeProcedureMapper recipeProcedureMapper;

    /**
     * 查询【请填写功能名称】
     * 
     * @param recipeId 【请填写功能名称】主键
     * @return 【请填写功能名称】
     */
    @Override
    public RecipeProcedure selectRecipeProcedureByRecipeId(Long recipeId)
    {
        return recipeProcedureMapper.selectRecipeProcedureByRecipeId(recipeId);
    }

    /**
     * 查询【请填写功能名称】列表
     * 
     * @param recipeProcedure 【请填写功能名称】
     * @return 【请填写功能名称】
     */
    @Override
    public List<RecipeProcedure> selectRecipeProcedureList(RecipeProcedure recipeProcedure)
    {
        return recipeProcedureMapper.selectRecipeProcedureList(recipeProcedure);
    }

    /**
     * 新增【请填写功能名称】
     * 
     * @param recipeProcedure 【请填写功能名称】
     * @return 结果
     */
    @Override
    public int insertRecipeProcedure(RecipeProcedure recipeProcedure)
    {
        return recipeProcedureMapper.insertRecipeProcedure(recipeProcedure);
    }

    /**
     * 修改【请填写功能名称】
     * 
     * @param recipeProcedure 【请填写功能名称】
     * @return 结果
     */
    @Override
    public int updateRecipeProcedure(RecipeProcedure recipeProcedure)
    {
        return recipeProcedureMapper.updateRecipeProcedure(recipeProcedure);
    }

    /**
     * 批量删除【请填写功能名称】
     * 
     * @param recipeIds 需要删除的【请填写功能名称】主键
     * @return 结果
     */
    @Override
    public int deleteRecipeProcedureByRecipeIds(Long[] recipeIds)
    {
        return recipeProcedureMapper.deleteRecipeProcedureByRecipeIds(recipeIds);
    }

    /**
     * 删除【请填写功能名称】信息
     * 
     * @param recipeId 【请填写功能名称】主键
     * @return 结果
     */
    @Override
    public int deleteRecipeProcedureByRecipeId(Long recipeId)
    {
        return recipeProcedureMapper.deleteRecipeProcedureByRecipeId(recipeId);
    }
}
