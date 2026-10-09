package com.ruoyi.web.controller.system;

import java.util.List;
import javax.servlet.http.HttpServletResponse;

import com.ruoyi.common.annotation.Anonymous;
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
import com.ruoyi.system.domain.RecipeIngredient;
import com.ruoyi.system.service.IRecipeIngredientService;
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
@RequestMapping("/system/ingredient")
public class RecipeIngredientController extends BaseController
{
    @Autowired
    private IRecipeIngredientService recipeIngredientService;

    /**
     * 查询【请填写功能名称】列表
     */
    @PreAuthorize("@ss.hasPermi('system:ingredient:list')")
    @GetMapping("/list")
    public TableDataInfo list(RecipeIngredient recipeIngredient)
    {
        startPage();
        List<RecipeIngredient> list = recipeIngredientService.selectRecipeIngredientList(recipeIngredient);
        return getDataTable(list);
    }

    /**
     * 导出【请填写功能名称】列表
     */
    @PreAuthorize("@ss.hasPermi('system:ingredient:export')")
    @Log(title = "【请填写功能名称】", businessType = BusinessType.EXPORT)
    @PostMapping("/export")
    public void export(HttpServletResponse response, RecipeIngredient recipeIngredient)
    {
        List<RecipeIngredient> list = recipeIngredientService.selectRecipeIngredientList(recipeIngredient);
        ExcelUtil<RecipeIngredient> util = new ExcelUtil<RecipeIngredient>(RecipeIngredient.class);
        util.exportExcel(response, list, "【请填写功能名称】数据");
    }

    /**
     * 获取【请填写功能名称】详细信息
     */
    @PreAuthorize("@ss.hasPermi('system:ingredient:query')")
    @GetMapping(value = "/{recipeId}")
    public AjaxResult getInfo(@PathVariable("recipeId") Long recipeId)
    {
        return success(recipeIngredientService.selectRecipeIngredientByRecipeId(recipeId));
    }

    /**
     * 新增【请填写功能名称】
     */
    @PreAuthorize("@ss.hasPermi('system:ingredient:add')")
    @Log(title = "【请填写功能名称】", businessType = BusinessType.INSERT)
    @PostMapping
    public AjaxResult add(@RequestBody RecipeIngredient recipeIngredient)
    {
        return toAjax(recipeIngredientService.insertRecipeIngredient(recipeIngredient));
    }

    /**
     * 修改【请填写功能名称】
     */
    @PreAuthorize("@ss.hasPermi('system:ingredient:edit')")
    @Log(title = "【请填写功能名称】", businessType = BusinessType.UPDATE)
    @PutMapping
    public AjaxResult edit(@RequestBody RecipeIngredient recipeIngredient)
    {
        return toAjax(recipeIngredientService.updateRecipeIngredient(recipeIngredient));
    }

    /**
     * 删除【请填写功能名称】
     */
    @PreAuthorize("@ss.hasPermi('system:ingredient:remove')")
    @Log(title = "【请填写功能名称】", businessType = BusinessType.DELETE)
	@DeleteMapping("/{recipeIds}")
    public AjaxResult remove(@PathVariable Long[] recipeIds)
    {
        return toAjax(recipeIngredientService.deleteRecipeIngredientByRecipeIds(recipeIds));
    }
}
