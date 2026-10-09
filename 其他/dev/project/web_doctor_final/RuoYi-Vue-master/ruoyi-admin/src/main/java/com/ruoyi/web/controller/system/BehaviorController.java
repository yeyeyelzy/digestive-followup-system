package com.ruoyi.web.controller.system;

import java.util.List;
import javax.servlet.http.HttpServletResponse;

import com.ruoyi.common.annotation.Anonymous;
import com.ruoyi.common.core.domain.model.LoginUser;
import com.ruoyi.system.domain.Diet;
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
import com.ruoyi.system.domain.Behavior;
import com.ruoyi.system.service.IBehaviorService;
import com.ruoyi.common.utils.poi.ExcelUtil;
import com.ruoyi.common.core.page.TableDataInfo;

/**
 * 行为日记管理Controller
 * 
 * @author ruoyi
 * @date 2023-07-11
 */
@RestController
//@Anonymous
@RequestMapping("/system/behavior")
public class BehaviorController extends BaseController
{
    @Autowired
    private IBehaviorService behaviorService;

    /**
     * 查询行为日记管理列表
     */
//    @PreAuthorize("@ss.hasPermi('system:behavior:list')")
    @GetMapping("/list")
    public TableDataInfo list(Behavior behavior)
    {
        startPage();
        List<Behavior> list = behaviorService.selectBehaviorList(behavior);
        return getDataTable(list);
    }

    /**
     * 查询当前登录患者的行为日记列表
     */
    @GetMapping("/my-list")
    public TableDataInfo myList(Behavior behavior)
    {
        Long unifiedPatientId = getLoginUser().getUserId();
        behavior.setPatientId(unifiedPatientId);
        startPage();
        List<Behavior> list = behaviorService.selectBehaviorList(behavior);
        return getDataTable(list);
    }

    /**
     * 导出行为日记管理列表
     */
    @PreAuthorize("@ss.hasPermi('system:behavior:export')")
    @Log(title = "行为日记管理", businessType = BusinessType.EXPORT)
    @PostMapping("/export")
    public void export(HttpServletResponse response, Behavior behavior)
    {
        List<Behavior> list = behaviorService.selectBehaviorList(behavior);
        ExcelUtil<Behavior> util = new ExcelUtil<Behavior>(Behavior.class);
        util.exportExcel(response, list, "行为日记管理数据");
    }

    /**
     * 获取行为日记管理详细信息
     */
    @PreAuthorize("@ss.hasPermi('system:behavior:query')")
    @GetMapping(value = "/{behaviorId}")
    public AjaxResult getInfo(@PathVariable("behaviorId") Long behaviorId)
    {
        return success(behaviorService.selectBehaviorByBehaviorId(behaviorId));
    }

    /**
     * 新增行为日记管理
     */
//    @PreAuthorize("@ss.hasPermi('system:behavior:add')")
    @Log(title = "行为日记管理", businessType = BusinessType.INSERT)
    @PostMapping
    public AjaxResult add(@RequestBody Behavior behavior)
    {
        // 1. 获取当前登录用户
        LoginUser loginUser = getLoginUser();

        // 2. 【核心】获取统一的 Long ID 和 Patient Name
        Long unifiedPatientId = loginUser.getUserId();
        String patientName = loginUser.getUsername();
        // 3. 设置新增记录的 patientId 和 patientName
        behavior.setPatientId(unifiedPatientId);
        behavior.setPatientName(patientName);

        int count = behaviorService.searchByIdDate(behavior).size();
//        System.out.println(count);
        if (count>0)
            return toAjax(behaviorService.updateIdDate(behavior));
        else
            return toAjax(behaviorService.insertBehavior(behavior));
    }

    /**
     * 修改行为日记管理
     */
    @PreAuthorize("@ss.hasPermi('system:behavior:edit')")
    @Log(title = "行为日记管理", businessType = BusinessType.UPDATE)
    @PutMapping
    public AjaxResult edit(@RequestBody Behavior behavior)
    {
        if (!getLoginUser().getUserId().equals(behavior.getPatientId())) {
            return AjaxResult.error("无权修改非本人的记录");
        }
        return toAjax(behaviorService.updateBehavior(behavior));
    }

    /**
     * 删除行为日记管理
     */
    @PreAuthorize("@ss.hasPermi('system:behavior:remove')")
    @Log(title = "行为日记管理", businessType = BusinessType.DELETE)
	@DeleteMapping("/{behaviorIds}")
    public AjaxResult remove(@PathVariable Long[] behaviorIds)
    {
        return toAjax(behaviorService.deleteBehaviorByBehaviorIds(behaviorIds));
    }
}
