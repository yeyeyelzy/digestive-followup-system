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
import com.ruoyi.system.domain.RecipeProcedure;
import com.ruoyi.system.service.IRecipeProcedureService;
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
@RequestMapping("/system/procedure")
public class RecipeProcedureController extends BaseController
{
    @Autowired
    private IRecipeProcedureService recipeProcedureService;

    /**
     * 查询【请填写功能名称】列表
     */
    @PreAuthorize("@ss.hasPermi('system:procedure:list')")
    @GetMapping("/list")
    public TableDataInfo list(RecipeProcedure recipeProcedure)
    {
        startPage();
        List<RecipeProcedure> list = recipeProcedureService.selectRecipeProcedureList(recipeProcedure);
        return getDataTable(list);
    }

    /**
     * 导出【请填写功能名称】列表
     */
    @PreAuthorize("@ss.hasPermi('system:procedure:export')")
    @Log(title = "【请填写功能名称】", businessType = BusinessType.EXPORT)
    @PostMapping("/export")
    public void export(HttpServletResponse response, RecipeProcedure recipeProcedure)
    {
        List<RecipeProcedure> list = recipeProcedureService.selectRecipeProcedureList(recipeProcedure);
        ExcelUtil<RecipeProcedure> util = new ExcelUtil<RecipeProcedure>(RecipeProcedure.class);
        util.exportExcel(response, list, "【请填写功能名称】数据");
    }

    /**
     * 获取【请填写功能名称】详细信息
     */
    @PreAuthorize("@ss.hasPermi('system:procedure:query')")
    @GetMapping(value = "/{recipeId}")
    public AjaxResult getInfo(@PathVariable("recipeId") Long recipeId)
    {
        return success(recipeProcedureService.selectRecipeProcedureByRecipeId(recipeId));
    }

    /**
     * 新增【请填写功能名称】
     */
    @PreAuthorize("@ss.hasPermi('system:procedure:add')")
    @Log(title = "【请填写功能名称】", businessType = BusinessType.INSERT)
    @PostMapping
    public AjaxResult add(@RequestBody RecipeProcedure recipeProcedure)
    {
        return toAjax(recipeProcedureService.insertRecipeProcedure(recipeProcedure));
    }

    /**
     * 修改【请填写功能名称】
     */
    @PreAuthorize("@ss.hasPermi('system:procedure:edit')")
    @Log(title = "【请填写功能名称】", businessType = BusinessType.UPDATE)
    @PutMapping
    public AjaxResult edit(@RequestBody RecipeProcedure recipeProcedure)
    {
        return toAjax(recipeProcedureService.updateRecipeProcedure(recipeProcedure));
    }

    /**
     * 删除【请填写功能名称】
     */
    @PreAuthorize("@ss.hasPermi('system:procedure:remove')")
    @Log(title = "【请填写功能名称】", businessType = BusinessType.DELETE)
	@DeleteMapping("/{recipeIds}")
    public AjaxResult remove(@PathVariable Long[] recipeIds)
    {
        return toAjax(recipeProcedureService.deleteRecipeProcedureByRecipeIds(recipeIds));
    }
}
