package kr.ai.lineosft.projectmanagement.api.project.service;

import kr.ai.lineosft.projectmanagement.api.project.dto.PhaseRequest;
import kr.ai.lineosft.projectmanagement.api.project.dto.PhaseResponse;
import kr.ai.lineosft.projectmanagement.domain.project.entity.Phase;
import kr.ai.lineosft.projectmanagement.domain.project.entity.Project;
import kr.ai.lineosft.projectmanagement.domain.project.repository.PhaseRepository;
import kr.ai.lineosft.projectmanagement.domain.project.repository.ProjectRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class PhaseService {

    private final PhaseRepository phaseRepository;
    private final ProjectRepository projectRepository;

    public List<PhaseResponse> getPhases(Long projectId) {
        return phaseRepository.findByProjectId(projectId).stream()
                .map(PhaseResponse::new)
                .collect(Collectors.toList());
    }

    @Transactional
    public PhaseResponse createPhase(Long projectId, PhaseRequest request) {
        Project project = projectRepository.findById(projectId)
                .orElseThrow(() -> new IllegalArgumentException("프로젝트를 찾을 수 없습니다."));

        Phase phase = Phase.builder()
                .name(request.getName())
                .description(request.getDescription())
                .startDate(request.getStartDate())
                .endDate(request.getEndDate())
                .progress(request.getProgress())
                .project(project)
                .build();

        Phase savedPhase = phaseRepository.save(phase);
        return new PhaseResponse(savedPhase);
    }

    @Transactional
    public PhaseResponse updatePhase(Long phaseId, PhaseRequest request) {
        Phase phase = phaseRepository.findById(phaseId)
                .orElseThrow(() -> new IllegalArgumentException("단계를 찾을 수 없습니다."));

        phase.update(
                request.getName(),
                request.getDescription(),
                request.getStartDate(),
                request.getEndDate(),
                request.getProgress()
        );

        return new PhaseResponse(phase);
    }

    @Transactional
    public void deletePhase(Long phaseId) {
        Phase phase = phaseRepository.findById(phaseId)
                .orElseThrow(() -> new IllegalArgumentException("단계를 찾을 수 없습니다."));
        phaseRepository.delete(phase);
    }
}
