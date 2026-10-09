package com.ruoyi.system.service.impl;

import java.util.List;
import com.ruoyi.common.utils.DateUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.ruoyi.system.mapper.RecipeMapper;
import com.ruoyi.system.domain.Recipe;
import com.ruoyi.system.service.IRecipeService;

/**
 * 【请填写功能名称】Service业务层处理
 * 
 * @author ruoyi
 * @date 2023-07-14
 */
@Service
public class RecipeServiceImpl implements IRecipeService 
{
    @Autowired
    private RecipeMapper recipeMapper;

    /**
     * 查询【请填写功能名称】
     * 
     * @param recipeId 【请填写功能名称】主键
     * @return 【请填写功能名称】
     */
    @Override
    public Recipe selectRecipeByRecipeId(Long recipeId)
    {
        return recipeMapper.selectRecipeByRecipeId(recipeId);
    }

    /**
     * 查询【请填写功能名称】列表
     * 
     * @param recipe 【请填写功能名称】
     * @return 【请填写功能名称】
     */
    @Override
    public List<Recipe> selectRecipeList(Recipe recipe)
    {
        return recipeMapper.selectRecipeList(recipe);
    }

    /**
     * 新增【请填写功能名称】
     * 
     * @param recipe 【请填写功能名称】
     * @return 结果
     */
    @Override
    public int insertRecipe(Recipe recipe)
    {
        recipe.setCreateTime(DateUtils.getNowDate());
        return recipeMapper.insertRecipe(recipe);
    }

    /**
     * 修改【请填写功能名称】
     * 
     * @param recipe 【请填写功能名称】
     * @return 结果
     */
    @Override
    public int updateRecipe(Recipe recipe)
    {
        recipe.setUpdateTime(DateUtils.getNowDate());
        return recipeMapper.updateRecipe(recipe);
    }

    /**
     * 批量删除【请填写功能名称】
     * 
     * @param recipeIds 需要删除的【请填写功能名称】主键
     * @return 结果
     */
    @Override
    public int deleteRecipeByRecipeIds(Long[] recipeIds)
    {
        return recipeMapper.deleteRecipeByRecipeIds(recipeIds);
    }

    /**
     * 删除【请填写功能名称】信息
     * 
     * @param recipeId 【请填写功能名称】主键
     * @return 结果
     */
    @Override
    public int deleteRecipeByRecipeId(Long recipeId)
    {
        return recipeMapper.deleteRecipeByRecipeId(recipeId);
    }
}
