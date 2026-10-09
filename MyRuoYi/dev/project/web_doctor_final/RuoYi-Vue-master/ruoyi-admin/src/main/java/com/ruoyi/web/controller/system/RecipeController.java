package com.ruoyi.web.controller.system;

import java.util.List;
import javax.servlet.http.HttpServletResponse;

import com.ruoyi.common.annotation.Anonymous;
import com.ruoyi.system.domain.RecipeIngredient;
import com.ruoyi.system.domain.RecipeProcedure;
import com.ruoyi.system.service.IRecipeIngredientService;
import com.ruoyi.system.service.IRecipeProcedureService;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import com.ruoyi.common.annotation.Log;
import com.ruoyi.common.core.controller.BaseController;
import com.ruoyi.common.core.domain.AjaxResult;
import com.ruoyi.common.enums.BusinessType;
import com.ruoyi.system.domain.Recipe;
import com.ruoyi.system.service.IRecipeService;
import com.ruoyi.common.utils.poi.ExcelUtil;
import com.ruoyi.common.core.page.TableDataInfo;

/**
 * 【请填写功能名称】Controller
 * 
 * @author ruoyi
 * @date 2023-07-14
 */
@RestController
@Anonymous
@RequestMapping("/system/recipe")
public class RecipeController extends BaseController
{
    @Autowired
    private IRecipeService recipeService;
    @Autowired
    private IRecipeProcedureService recipeProcedureService;
    @Autowired
    private IRecipeIngredientService recipeIngredientService;

    @GetMapping("/{id}")
    public AjaxResult findOne(@PathVariable Long id) {
        Recipe recipe = recipeService.selectRecipeByRecipeId(id);
//        List<RecipeTag> tags = recipeTagMapper.selectByRecipeId(id);
//        for (RecipeTag t : tags) {
//            String name = tagMapper.selectNameById(t.getTagId());
//            t.setTagName(name);
//        }
        RecipeIngredient recipeIngredient=new RecipeIngredient();
        recipeIngredient.setRecipeId(id);
        List<RecipeIngredient> ingredients = recipeIngredientService.selectRecipeIngredientList(recipeIngredient);
//        for (RecipeIngredient i : ingredients) {
//            String name = ingredientMapper.selectNameById(i.getIngredientId());
//            i.setIngredientName(name);
//        }
        RecipeProcedure recipeProcedure=new RecipeProcedure();
        recipeProcedure.setRecipeId(id);
        List<RecipeProcedure> procedures = recipeProcedureService.selectRecipeProcedureList(recipeProcedure);
//        recipe.setTags(tags);
        recipe.setIngredients(ingredients);
        recipe.setProcedures(procedures);
//        recipe.setAuthorName(userMapper.selectNameById(recipe.getAuthorId()));
//        recipe.setAvatarUrl(userMapper.selectUrlById(recipe.getAuthorId()));
        return success(recipe);
    }

    /**
     * 查询【请填写功能名称】列表
     */
    @PreAuthorize("@ss.hasPermi('system:recipe:list')")
    @GetMapping("/list")
    public TableDataInfo list(Recipe recipe)
    {
        startPage();
        List<Recipe> list = recipeService.selectRecipeList(recipe);
        return getDataTable(list);
    }

    /**
     * 导出【请填写功能名称】列表
     */
    @PreAuthorize("@ss.hasPermi('system:recipe:export')")
    @Log(title = "【请填写功能名称】", businessType = BusinessType.EXPORT)
    @PostMapping("/export")
    public void export(HttpServletResponse response, Recipe recipe)
    {
        List<Recipe> list = recipeService.selectRecipeList(recipe);
        ExcelUtil<Recipe> util = new ExcelUtil<Recipe>(Recipe.class);
        util.exportExcel(response, list, "【请填写功能名称】数据");
    }

//    /**
//     * 获取【请填写功能名称】详细信息
//     */
//    @PreAuthorize("@ss.hasPermi('system:recipe:query')")
//    @GetMapping(value = "/{recipeId}")
//    public AjaxResult getInfo(@PathVariable("recipeId") Long recipeId)
//    {
//        return success(recipeService.selectRecipeByRecipeId(recipeId));
//    }

    /**
     * 新增【请填写功能名称】
     */
    @PreAuthorize("@ss.hasPermi('system:recipe:add')")
    @Log(title = "【请填写功能名称】", businessType = BusinessType.INSERT)
    @PostMapping
    public AjaxResult add(@RequestBody Recipe recipe)
    {
        return toAjax(recipeService.insertRecipe(recipe));
    }

    /**
     * 修改【请填写功能名称】
     */
    @PreAuthorize("@ss.hasPermi('system:recipe:edit')")
    @Log(title = "【请填写功能名称】", businessType = BusinessType.UPDATE)
    @PutMapping
    public AjaxResult edit(@RequestBody Recipe recipe)
    {
        return toAjax(recipeService.updateRecipe(recipe));
    }

    /**
     * 删除【请填写功能名称】
     */
//    @PreAuthorize("@ss.hasPermi('system:recipe:remove')")
//    @Log(title = "【请填写功能名称】", businessType = BusinessType.DELETE)
//	@DeleteMapping("/{recipeIds}")
//    public AjaxResult remove(@PathVariable Long[] recipeIds)
//    {
//        return toAjax(recipeService.deleteRecipeByRecipeIds(recipeIds));
//    }
}
