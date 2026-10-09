package com.ruoyi.web.controller.system;

import java.util.List;
import javax.servlet.http.HttpServletResponse;

import com.ruoyi.common.annotation.Anonymous;
import com.ruoyi.common.core.domain.model.LoginUser;
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
import com.ruoyi.system.domain.Diet;
import com.ruoyi.system.service.IDietService;
import com.ruoyi.common.utils.poi.ExcelUtil;
import com.ruoyi.common.core.page.TableDataInfo;

/**
 * 饮食日记管理Controller
 *
 * @author ruoyi
 * @date 2023-07-11
 */
@RestController

@RequestMapping("/system/diet")
public class DietController extends BaseController
{
    @Autowired
    private IDietService dietService;

    /**
     * 查询饮食日记管理列表
     */
    @GetMapping("/list")
    public TableDataInfo list(Diet diet)
    {
        startPage();
        List<Diet> list = dietService.selectDietList(diet);
        return getDataTable(list);
    }

    /**
     * 查询当前登录患者的饮食日记列表
     */
    @GetMapping("/my-list")
    public TableDataInfo myList(Diet diet)
    {
        Long unifiedPatientId = getLoginUser().getUserId();
        diet.setPatientId(unifiedPatientId);
        startPage();
        List<Diet> list = dietService.selectDietList(diet);
        return getDataTable(list);
    }

    // 导出功能通常只用于后台管理，保留权限注解
    @PreAuthorize("@ss.hasPermi('system:diet:export')")
    @Log(title = "饮食日记管理", businessType = BusinessType.EXPORT)
    @PostMapping("/export")
    public void export(HttpServletResponse response, Diet diet)
    {
        List<Diet> list = dietService.selectDietList(diet);
        ExcelUtil<Diet> util = new ExcelUtil<Diet>(Diet.class);
        util.exportExcel(response, list, "饮食日记管理数据");
    }

    // 获取详细信息 (通常是后台管理功能，保留权限注解)
    @PreAuthorize("@ss.hasPermi('system:diet:query')")
    @GetMapping(value = "/{dietId}")
    public AjaxResult getInfo(@PathVariable("dietId") Long dietId)
    {
        return success(dietService.selectDietByDietId(dietId));
    }

    /**
     * 新增饮食日记管理 (面向病人应用)
     */
    @Log(title = "饮食日记管理", businessType = BusinessType.INSERT)
    @PostMapping
    public AjaxResult add(@RequestBody Diet diet)
    {
        // 1. 获取当前登录用户
        LoginUser loginUser = getLoginUser();

        // 2. 【核心】获取统一的 Long ID 和 Patient Name
        Long unifiedPatientId = loginUser.getUserId();
        String patientName = loginUser.getUsername();
        // 3. 设置新增记录的 patientId 和 patientName
        diet.setPatientId(unifiedPatientId);
        diet.setPatientName(patientName);

        if (dietService.searchByIdDate(diet).size() == 0)
            return toAjax(dietService.insertDiet(diet));
        else
            return toAjax(dietService.updateIdDate(diet));
    }

    // 修改和删除通常也用于后台管理，建议保留权限注解，或者根据病人需求进行修改。
    @PreAuthorize("@ss.hasPermi('system:diet:edit')")
    @Log(title = "饮食日记管理", businessType = BusinessType.UPDATE)
    @PutMapping
    public AjaxResult edit(@RequestBody Diet diet)
    {
        // 【注意】为了安全，修改操作也应该检查ID是否匹配，防止病人修改其他人的数据。
        if (!getLoginUser().getUserId().equals(diet.getPatientId())) {
            return AjaxResult.error("无权修改非本人的记录");
        }
        return toAjax(dietService.updateDiet(diet));
    }

    @PreAuthorize("@ss.hasPermi('system:diet:remove')")
    @Log(title = "饮食日记管理", businessType = BusinessType.DELETE)
    @DeleteMapping("/{dietIds}")
    public AjaxResult remove(@PathVariable Long[] dietIds)
    {
        // 【注意】这里需要检查 dietIds 对应记录的 patientId 是否属于当前用户，否则可能误删。
        return toAjax(dietService.deleteDietByDietIds(dietIds));
    }
}

