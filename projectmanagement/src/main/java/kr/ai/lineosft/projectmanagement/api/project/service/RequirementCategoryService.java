package kr.ai.lineosft.projectmanagement.api.project.service;

import kr.ai.lineosft.projectmanagement.api.project.dto.RequirementCategoryResponse;
import kr.ai.lineosft.projectmanagement.domain.project.entity.Project;
import kr.ai.lineosft.projectmanagement.domain.project.entity.RequirementCategory;
import kr.ai.lineosft.projectmanagement.domain.project.repository.ProjectRepository;
import kr.ai.lineosft.projectmanagement.domain.project.repository.RequirementCategoryRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class RequirementCategoryService {

    private final RequirementCategoryRepository categoryRepository;
    private final ProjectRepository projectRepository;

    @Transactional
    public List<RequirementCategoryResponse> getCategories(Long projectId) {
        seedDefaultCategories();

        return categoryRepository.findByProjectIdOrGlobal(projectId).stream()
                .map(RequirementCategoryResponse::new)
                .collect(Collectors.toList());
    }

    @Transactional
    public RequirementCategoryResponse createCategory(Long projectId, String name) {
        Project project = projectRepository.findById(projectId)
                .orElseThrow(() -> new IllegalArgumentException("프로젝트를 찾을 수 없습니다."));

        // Check if category name already exists for this project (or globally)
        boolean exists = categoryRepository.findByProjectIdOrGlobal(projectId).stream()
                .anyMatch(c -> c.getName().equalsIgnoreCase(name));
        if (exists) {
            throw new IllegalArgumentException("이미 존재하는 카테고리입니다.");
        }

        RequirementCategory category = RequirementCategory.builder()
                .name(name)
                .project(project)
                .build();

        RequirementCategory saved = categoryRepository.save(category);
        return new RequirementCategoryResponse(saved);
    }

    private void seedDefaultCategories() {
        if (categoryRepository.count() == 0) {
            categoryRepository.save(RequirementCategory.builder().name("기능").build());
            categoryRepository.save(RequirementCategory.builder().name("비기능").build());
            categoryRepository.save(RequirementCategory.builder().name("UI/UX").build());
            categoryRepository.save(RequirementCategory.builder().name("보안").build());
            categoryRepository.save(RequirementCategory.builder().name("인터페이스").build());
        }
    }
}
