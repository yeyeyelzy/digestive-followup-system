package com.ruoyi.system.service.impl;

import java.util.List;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.ruoyi.system.mapper.RecipeIngredientMapper;
import com.ruoyi.system.domain.RecipeIngredient;
import com.ruoyi.system.service.IRecipeIngredientService;

/**
 * 【请填写功能名称】Service业务层处理
 * 
 * @author ruoyi
 * @date 2023-07-14
 */
@Service
public class RecipeIngredientServiceImpl implements IRecipeIngredientService 
{
    @Autowired
    private RecipeIngredientMapper recipeIngredientMapper;

    /**
     * 查询【请填写功能名称】
     * 
     * @param recipeId 【请填写功能名称】主键
     * @return 【请填写功能名称】
     */
    @Override
    public RecipeIngredient selectRecipeIngredientByRecipeId(Long recipeId)
    {
        return recipeIngredientMapper.selectRecipeIngredientByRecipeId(recipeId);
    }

    /**
     * 查询【请填写功能名称】列表
     * 
     * @param recipeIngredient 【请填写功能名称】
     * @return 【请填写功能名称】
     */
    @Override
    public List<RecipeIngredient> selectRecipeIngredientList(RecipeIngredient recipeIngredient)
    {
        return recipeIngredientMapper.selectRecipeIngredientList(recipeIngredient);
    }

    /**
     * 新增【请填写功能名称】
     * 
     * @param recipeIngredient 【请填写功能名称】
     * @return 结果
     */
    @Override
    public int insertRecipeIngredient(RecipeIngredient recipeIngredient)
    {
        return recipeIngredientMapper.insertRecipeIngredient(recipeIngredient);
    }

    /**
     * 修改【请填写功能名称】
     * 
     * @param recipeIngredient 【请填写功能名称】
     * @return 结果
     */
    @Override
    public int updateRecipeIngredient(RecipeIngredient recipeIngredient)
    {
        return recipeIngredientMapper.updateRecipeIngredient(recipeIngredient);
    }

    /**
     * 批量删除【请填写功能名称】
     * 
     * @param recipeIds 需要删除的【请填写功能名称】主键
     * @return 结果
     */
    @Override
    public int deleteRecipeIngredientByRecipeIds(Long[] recipeIds)
    {
        return recipeIngredientMapper.deleteRecipeIngredientByRecipeIds(recipeIds);
    }

    /**
     * 删除【请填写功能名称】信息
     * 
     * @param recipeId 【请填写功能名称】主键
     * @return 结果
     */
    @Override
    public int deleteRecipeIngredientByRecipeId(Long recipeId)
    {
        return recipeIngredientMapper.deleteRecipeIngredientByRecipeId(recipeId);
    }
}
