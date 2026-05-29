package kr.ai.lineosft.projectmanagement.api.project.service;

import kr.ai.lineosft.projectmanagement.api.project.dto.SprintRequest;
import kr.ai.lineosft.projectmanagement.api.project.dto.SprintResponse;
import kr.ai.lineosft.projectmanagement.domain.project.entity.Project;
import kr.ai.lineosft.projectmanagement.domain.project.entity.Sprint;
import kr.ai.lineosft.projectmanagement.domain.project.repository.ProjectRepository;
import kr.ai.lineosft.projectmanagement.domain.project.repository.SprintRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class SprintService {

    private final SprintRepository sprintRepository;
    private final ProjectRepository projectRepository;

    public List<SprintResponse> getSprints(Long projectId) {
        return sprintRepository.findByProjectId(projectId).stream()
                .map(SprintResponse::new)
                .collect(Collectors.toList());
    }

    @Transactional
    public SprintResponse createSprint(Long projectId, SprintRequest request) {
        Project project = projectRepository.findById(projectId)
                .orElseThrow(() -> new IllegalArgumentException("프로젝트를 찾을 수 없습니다."));

        Sprint sprint = Sprint.builder()
                .name(request.getName())
                .goal(request.getGoal())
                .startDate(request.getStartDate())
                .endDate(request.getEndDate())
                .status(request.getStatus())
                .project(project)
                .build();

        Sprint savedSprint = sprintRepository.save(sprint);
        return new SprintResponse(savedSprint);
    }

    @Transactional
    public SprintResponse updateSprint(Long sprintId, SprintRequest request) {
        Sprint sprint = sprintRepository.findById(sprintId)
                .orElseThrow(() -> new IllegalArgumentException("스프린트를 찾을 수 없습니다."));

        sprint.update(
                request.getName(),
                request.getGoal(),
                request.getStartDate(),
                request.getEndDate(),
                request.getStatus()
        );

        return new SprintResponse(sprint);
    }

    @Transactional
    public void deleteSprint(Long sprintId) {
        Sprint sprint = sprintRepository.findById(sprintId)
                .orElseThrow(() -> new IllegalArgumentException("스프린트를 찾을 수 없습니다."));
        sprintRepository.delete(sprint);
    }
}
