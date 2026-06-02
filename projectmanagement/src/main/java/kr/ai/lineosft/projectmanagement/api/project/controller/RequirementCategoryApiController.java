package kr.ai.lineosft.projectmanagement.api.project.controller;

import kr.ai.lineosft.projectmanagement.api.project.dto.RequirementCategoryResponse;
import kr.ai.lineosft.projectmanagement.api.project.service.RequirementCategoryService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequiredArgsConstructor
public class RequirementCategoryApiController {

    private final RequirementCategoryService categoryService;

    @GetMapping("/api/projects/{projectId}/requirement-categories")
    public ResponseEntity<List<RequirementCategoryResponse>> getCategories(@PathVariable Long projectId) {
        return ResponseEntity.ok(categoryService.getCategories(projectId));
    }

    @PostMapping("/api/projects/{projectId}/requirement-categories")
    public ResponseEntity<RequirementCategoryResponse> createCategory(
            @PathVariable Long projectId,
            @RequestParam String name) {
        RequirementCategoryResponse created = categoryService.createCategory(projectId, name);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }
}
