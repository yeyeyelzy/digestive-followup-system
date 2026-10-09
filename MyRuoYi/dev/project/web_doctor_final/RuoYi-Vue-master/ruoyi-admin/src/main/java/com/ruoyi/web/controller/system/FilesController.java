package com.ruoyi.web.controller.system;

import cn.hutool.core.io.FileUtil;
import cn.hutool.core.util.IdUtil;
import cn.hutool.core.util.StrUtil;
import cn.hutool.crypto.SecureUtil;

import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.net.URLEncoder;
import java.util.List;
import javax.servlet.ServletOutputStream;
import javax.servlet.http.HttpServletResponse;

import com.ruoyi.common.annotation.Anonymous;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import com.ruoyi.common.annotation.Log;
import com.ruoyi.common.core.controller.BaseController;
import com.ruoyi.common.core.domain.AjaxResult;
import com.ruoyi.common.enums.BusinessType;
import com.ruoyi.system.domain.Files;
import com.ruoyi.system.service.IFilesService;
import com.ruoyi.common.utils.poi.ExcelUtil;
import com.ruoyi.common.core.page.TableDataInfo;
import org.springframework.web.multipart.MultipartFile;

/**
 * 文件管理Controller
 *
 * @author ruoyi
 * @date 2023-07-11
 */
@RestController
@Anonymous
@RequestMapping("/system/files")
public class FilesController extends BaseController {
    @Autowired
    private IFilesService filesService;

    @Value("${files.upload.path}")
    private String fileUploadPath;

    @Value("${server.ip}")
    private String serverIp;

    @Value("${server.port}")
    private int serverPort;

    @Value("${files.public-base-url:}")
    private String publicBaseUrl;

    /**
     * 文件上传接口
     *
     * @param file 前端传递过来的文件
     * @return
     * @throws IOException
     */
    @PostMapping("/upload")
    public String upload(@RequestParam MultipartFile file) throws IOException {
        String originalFilename = file.getOriginalFilename();
        String type = FileUtil.extName(originalFilename);
        long size = file.getSize();

        // 定义一个文件唯一的标识码
        String fileUUID = IdUtil.fastSimpleUUID() + StrUtil.DOT + type;

        File uploadFile = new File(fileUploadPath + fileUUID);
        // 判断配置的文件目录是否存在，若不存在则创建一个新的文件目录
        File parentFile = uploadFile.getParentFile();
        if (!parentFile.exists()) {
            parentFile.mkdirs();
        }

        String url;
        InputStream is = file.getInputStream();
        // 获取文件的md5
        String md5 = SecureUtil.md5(is);
        is.close();
        // 从数据库查询是否存在相同的记录
        Files dbFiles = getFileByMd5(md5);
        if (dbFiles != null) {
            url = dbFiles.getUrl();
        } else {
            // 上传文件到磁盘
            file.transferTo(uploadFile);
            // 数据库若不存在重复文件，则不删除刚才上传的文件
            String baseUrl = StrUtil.isBlank(publicBaseUrl)
                    ? "http://" + serverIp + ":" + serverPort
                    : StrUtil.removeSuffix(publicBaseUrl, "/");
            url = baseUrl + "/system/files/" + fileUUID;
            // 存储数据库
            Files saveFile = new Files();
            saveFile.setName(originalFilename);
            saveFile.setType(type);
            saveFile.setSize(size / 1024); // 单位 kb
            saveFile.setUrl(url);
            saveFile.setMd5(md5);
            filesService.insertFiles(saveFile);
//            fileMapper.insert(saveFile);
        }
        // 从redis取出数据，操作完，再设置（不用查询数据库）
//        String json = stringRedisTemplate.opsForValue().get(Constants.FILES_KEY);
//        List<Files> files1 = JSONUtil.toBean(json, new TypeReference<List<Files>>() {
//        }, true);
//        files1.add(saveFile);
//        setCache(Constants.FILES_KEY, JSONUtil.toJsonStr(files1));


        // 从数据库查出数据
//        List<Files> files = fileMapper.selectList(null);
//        // 设置最新的缓存
//        setCache(Constants.FILES_KEY, JSONUtil.toJsonStr(files));

        // 最简单的方式：直接清空缓存
//        flushRedis(Constants.FILES_KEY);

        return url;
    }

    /**
     * 文件下载接口   http://localhost:8083/file/{fileUUID}
     *
     * @param fileUUID
     * @param response
     * @throws IOException
     */
    @GetMapping("/{fileUUID}")
    public void download(@PathVariable String fileUUID, HttpServletResponse response) throws IOException {
        // 根据文件的唯一标识码获取文件
        File uploadFile = new File(fileUploadPath + fileUUID);
        // 设置输出流的格式
        ServletOutputStream os = response.getOutputStream();
        response.addHeader("Content-Disposition", "attachment;filename=" + URLEncoder.encode(fileUUID, "UTF-8"));
        response.setContentType("application/octet-stream");

        // 读取文件的字节流
        os.write(FileUtil.readBytes(uploadFile));
        os.flush();
        os.close();
    }


    /**
     * 通过文件的md5查询文件
     *
     * @param md5
     * @return
     */
    private Files getFileByMd5(String md5) {
        // 查询文件的md5是否存在
        Files files = new Files();
        files.setMd5(md5);
        List<Files> filesList = filesService.selectFilesList(files);
        return filesList.size() == 0 ? null : filesList.get(0);
    }


    /**
     * 查询文件管理列表
     */
    @PreAuthorize("@ss.hasPermi('system:files:list')")
    @GetMapping("/list")
    public TableDataInfo list(Files files) {
        startPage();
        List<Files> list = filesService.selectFilesList(files);
        return getDataTable(list);
    }

    /**
     * 导出文件管理列表
     */
    @PreAuthorize("@ss.hasPermi('system:files:export')")
    @Log(title = "文件管理", businessType = BusinessType.EXPORT)
    @PostMapping("/export")
    public void export(HttpServletResponse response, Files files) {
        List<Files> list = filesService.selectFilesList(files);
        ExcelUtil<Files> util = new ExcelUtil<Files>(Files.class);
        util.exportExcel(response, list, "文件管理数据");
    }

    /**
     * 获取文件管理详细信息
     */
//    @PreAuthorize("@ss.hasPermi('system:files:query')")
//    @GetMapping(value = "/{id}")
//    public AjaxResult getInfo(@PathVariable("id") Long id)
//    {
//        return success(filesService.selectFilesById(id));
//    }

    /**
     * 新增文件管理
     */
    @PreAuthorize("@ss.hasPermi('system:files:add')")
    @Log(title = "文件管理", businessType = BusinessType.INSERT)
    @PostMapping
    public AjaxResult add(@RequestBody Files files) {
        return toAjax(filesService.insertFiles(files));
    }

    /**
     * 修改文件管理
     */
    @PreAuthorize("@ss.hasPermi('system:files:edit')")
    @Log(title = "文件管理", businessType = BusinessType.UPDATE)
    @PutMapping
    public AjaxResult edit(@RequestBody Files files) {
        return toAjax(filesService.updateFiles(files));
    }

    /**
     * 删除文件管理
     */
    @PreAuthorize("@ss.hasPermi('system:files:remove')")
    @Log(title = "文件管理", businessType = BusinessType.DELETE)
    @DeleteMapping("/{ids}")
    public AjaxResult remove(@PathVariable Long[] ids) {
        return toAjax(filesService.deleteFilesByIds(ids));
    }
}
