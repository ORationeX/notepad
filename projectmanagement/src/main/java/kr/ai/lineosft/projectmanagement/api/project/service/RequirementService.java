package kr.ai.lineosft.projectmanagement.api.project.service;

import kr.ai.lineosft.projectmanagement.api.project.dto.RequirementHistoryResponse;
import kr.ai.lineosft.projectmanagement.api.project.dto.RequirementRequest;
import kr.ai.lineosft.projectmanagement.api.project.dto.RequirementResponse;
import kr.ai.lineosft.projectmanagement.domain.member.entity.Member;
import kr.ai.lineosft.projectmanagement.domain.member.repository.MemberRepository;
import kr.ai.lineosft.projectmanagement.domain.project.entity.*;
import kr.ai.lineosft.projectmanagement.domain.project.repository.ProjectRepository;
import kr.ai.lineosft.projectmanagement.domain.project.repository.RequirementCategoryRepository;
import kr.ai.lineosft.projectmanagement.domain.project.repository.RequirementHistoryRepository;
import kr.ai.lineosft.projectmanagement.domain.project.repository.RequirementRepository;
import kr.ai.lineosft.projectmanagement.domain.project.repository.TaskRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class RequirementService {

    private final RequirementRepository requirementRepository;
    private final ProjectRepository projectRepository;
    private final MemberRepository memberRepository;
    private final TaskRepository taskRepository;
    private final RequirementCategoryRepository categoryRepository;
    private final RequirementHistoryRepository historyRepository;

    public List<RequirementResponse> getRequirements(Long projectId) {
        return requirementRepository.findByProjectIdWithRelations(projectId).stream()
                .map(RequirementResponse::new)
                .collect(Collectors.toList());
    }

    public RequirementResponse getRequirement(Long id) {
        Requirement requirement = requirementRepository.findByIdWithRelations(id)
                .orElseThrow(() -> new IllegalArgumentException("요구사항을 찾을 수 없습니다."));
        return new RequirementResponse(requirement);
    }

    public List<RequirementHistoryResponse> getHistories(Long id) {
        return historyRepository.findByRequirementIdOrderByModifiedAtDesc(id).stream()
                .map(RequirementHistoryResponse::new)
                .collect(Collectors.toList());
    }

    @Transactional
    public RequirementResponse createRequirement(Long projectId, RequirementRequest request, Member author) {
        Project project = projectRepository.findById(projectId)
                .orElseThrow(() -> new IllegalArgumentException("프로젝트를 찾을 수 없습니다."));

        if (request.getCategoryId() == null) {
            throw new IllegalArgumentException("요구사항 분류(카테고리)는 필수 선택 항목입니다.");
        }
        RequirementCategory category = categoryRepository.findById(request.getCategoryId())
                .orElseThrow(() -> new IllegalArgumentException("카테고리를 찾을 수 없습니다."));

        Member assignee = null;
        if (request.getAssigneeId() != null) {
            assignee = memberRepository.findById(request.getAssigneeId())
                    .orElseThrow(() -> new IllegalArgumentException("담당자를 찾을 수 없습니다."));
        }

        Requirement requirement = Requirement.builder()
                .requirementCode("TEMP")
                .title(request.getTitle())
                .description(request.getDescription())
                .category(category)
                .priority(request.getPriority())
                .status(request.getStatus() != null ? request.getStatus() : RequirementStatus.DRAFT)
                .progress(request.getProgress() != null ? request.getProgress() : 0)
                .project(project)
                .author(author)
                .assignee(assignee)
                .requestedBy(request.getRequestedBy())
                .domainName(request.getDomainName())
                .build();

        Requirement saved = requirementRepository.save(requirement);

        // Generate code
        String globalCode = String.format("REQ-%05d", saved.getId());
        saved.setRequirementCode(globalCode);

        // Record initial history snapshot
        saveHistorySnapshot(saved, author, "요구사항 등록됨");

        return new RequirementResponse(saved);
    }

    @Transactional
    public RequirementResponse updateRequirement(Long id, RequirementRequest request, Member modifier) {
        Requirement requirement = requirementRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("요구사항을 찾을 수 없습니다."));

        if (request.getCategoryId() == null) {
            throw new IllegalArgumentException("요구사항 분류(카테고리)는 필수 선택 항목입니다.");
        }
        RequirementCategory category = categoryRepository.findById(request.getCategoryId())
                .orElseThrow(() -> new IllegalArgumentException("카테고리를 찾을 수 없습니다."));

        Member assignee = null;
        if (request.getAssigneeId() != null) {
            assignee = memberRepository.findById(request.getAssigneeId())
                    .orElseThrow(() -> new IllegalArgumentException("담당자를 찾을 수 없습니다."));
        }

        requirement.update(
                request.getTitle(),
                request.getDescription(),
                category,
                request.getPriority(),
                request.getStatus(),
                request.getProgress(),
                assignee,
                request.getRequestedBy(),
                request.getDomainName()
        );

        // Record update history snapshot
        saveHistorySnapshot(requirement, modifier, "정보 수정됨");

        return new RequirementResponse(requirement);
    }

    @Transactional
    public void deleteRequirement(Long id) {
        Requirement requirement = requirementRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("요구사항을 찾을 수 없습니다."));

        // Unlink tasks
        List<Task> tasks = taskRepository.findByRequirementId(id);
        for (Task task : tasks) {
            task.linkRequirement(null);
        }

        // Delete associated history
        List<RequirementHistory> histories = historyRepository.findByRequirementIdOrderByModifiedAtDesc(id);
        historyRepository.deleteAll(histories);

        requirementRepository.delete(requirement);
    }

    @Transactional
    public RequirementResponse syncProgressFromTasks(Long id, Member modifier) {
        Requirement requirement = requirementRepository.findById(id)
                .orElseThrow(() -> new IllegalArgumentException("요구사항을 찾을 수 없습니다."));
        List<Task> tasks = taskRepository.findByRequirementId(id);
        if (!tasks.isEmpty()) {
            int sum = tasks.stream().mapToInt(Task::getProgress).sum();
            int avg = sum / tasks.size();
            Integer oldProgress = requirement.getProgress();
            if (!oldProgress.equals(avg)) {
                requirement.updateProgress(avg);
                saveHistorySnapshot(requirement, modifier, "태스크 진행률 기준 자동 계산 동기화 (" + oldProgress + "% -> " + avg + "%)");
            }
        }
        return new RequirementResponse(requirement);
    }

    @Transactional
    public void syncStatusFromTasks(Requirement requirement, Member modifier) {
        if (requirement == null) return;

        List<Task> tasks = taskRepository.findByRequirementId(requirement.getId());
        if (tasks.isEmpty()) return;

        boolean anyInProgress = false;
        boolean allDone = true;

        for (Task task : tasks) {
            if (task.getStatus() == TaskStatus.IN_PROGRESS) {
                anyInProgress = true;
            }
            if (task.getStatus() != TaskStatus.DONE) {
                allDone = false;
            }
        }

        RequirementStatus oldStatus = requirement.getStatus();
        RequirementStatus newStatus = null;

        if (allDone) {
            newStatus = RequirementStatus.COMPLETED;
        } else if (anyInProgress) {
            newStatus = RequirementStatus.DEVELOPING;
        }

        if (newStatus != null && oldStatus != newStatus) {
            requirement.updateStatus(newStatus);
            requirementRepository.save(requirement);
            saveHistorySnapshot(requirement, modifier, "태스크 상태 변경에 의한 상태 자동 전환 (" + oldStatus.getDescription() + " -> " + newStatus.getDescription() + ")");
        }
    }

    private void saveHistorySnapshot(Requirement requirement, Member modifier, String comment) {
        RequirementHistory history = RequirementHistory.builder()
                .requirement(requirement)
                .title(requirement.getTitle())
                .description(requirement.getDescription())
                .category(requirement.getCategory())
                .priority(requirement.getPriority())
                .status(requirement.getStatus())
                .progress(requirement.getProgress())
                .requestedBy(requirement.getRequestedBy())
                .domainName(requirement.getDomainName())
                .modifier(modifier)
                .comment(comment)
                .build();
        historyRepository.save(history);
    }
}
